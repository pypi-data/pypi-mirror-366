import threading
from photo_culling.utils import load_image_with_exif, clip, resize_img_with_padding


class ImageCache:
    def __init__(self, fnames):
        self.preview_range = (-100, 100)
        self.full_range = (-5, 15)
        self.prefetch_order = self._build_prefetch_order()
        self.fnames = fnames
        self.full_images = {}
        self.previews = {}
        self.lock_full = threading.Lock()
        self.lock_preview = threading.Lock()

    def clean_cache(self, current_idx, current_res):
        with self.lock_full:
            full_keys = list(self.full_images.keys())
            for idx in full_keys:
                offset = idx - current_idx
                if not (self.full_range[0] <= offset <= self.full_range[1]):
                    del self.full_images[idx]

        with self.lock_preview:
            preview_keys = list(self.previews.keys())
            for key in preview_keys:
                offset = key[0] - current_idx
                if not ((key[1:] == current_res) and (self.preview_range[0] <= offset <= self.preview_range[1])):
                    del self.previews[key]

    def load_next_required_item(self, current_idx, current_res):
        for full, offset in self.prefetch_order:
            idx = clip(current_idx + offset, 0, len(self.fnames))
            if full and (idx not in self.full_images):
                self.get_full_image(idx)
                return True
            if (not full) and (idx, *current_res) not in self.previews:
                self.get_preview(idx, current_res)
                return True
        return False

    def get_full_image(self, idx):
        if idx in self.full_images:
            return self.full_images[idx]
        with self.lock_full:
            # While waiting for the lock, the image might have been prefetched; try cache again
            if idx in self.full_images:
                return self.full_images[idx]
            img = load_image_with_exif(self.fnames[idx])
            self.full_images[idx] = img
            return img

    def get_preview(self, idx, resolution):
        cache_id = (idx, *resolution)
        if cache_id in self.previews:
            return self.previews[cache_id]
        with self.lock_preview:
            # While waiting for the lock, the image might have been prefetched; try cache again
            if cache_id in self.previews:
                return self.previews[cache_id]
            full = self.get_full_image(idx)
            preview = resize_img_with_padding(full, resolution)
            self.previews[cache_id] = preview
            return preview

    def _build_prefetch_order(self):
        prefetch_order = []

        # Most important images, which should be fetched in this order
        priority_offsets = [0, 1, -1, 2, 3, 10, -2, -3, -10, 4, -4, 5, -5, 20]
        for i in priority_offsets:
            prefetch_order.append((True, i))
            prefetch_order.append((False, i))

        # Other offsets, ordered starting closest to current image
        other_offsets = list(
            range(min(self.full_range[0], self.preview_range[0]), max(self.full_range[1], self.preview_range[1]) + 1)
        )
        other_offsets = sorted(other_offsets, key=abs)
        for i in other_offsets:
            if (self.full_range[0] <= i <= self.full_range[1]) and (True, i) not in prefetch_order:
                prefetch_order.append((True, i))
            if (self.preview_range[0] <= i <= self.preview_range[1]) and (False, i) not in prefetch_order:
                prefetch_order.append((False, i))
        return prefetch_order
