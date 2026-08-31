"""Raw binary header parser for image metadata extraction.
Copyright © 2026 - Present, John Liu
"""

import struct

from batch_img.const import UNKNOWN


# pylint: disable=too-few-public-methods
class Exif:
    """Extract metadata directly from raw image header bytes."""

    @staticmethod
    def _parse_png(data: bytes) -> dict:
        if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) < 26:
            return {}
        w, h, bit_depth, color_type = struct.unpack(">IIBB", data[16:26])
        color_modes = {0: "L", 2: "RGB", 3: "P", 4: "LA", 6: "RGBA"}
        return {
            "format": "PNG",
            "size": (w, h),
            "bit_depth": bit_depth,
            "mode": color_modes.get(color_type, UNKNOWN),
        }

    @staticmethod
    def _parse_jpeg_chroma(comp: bytes) -> str | None:
        y_samp, cb_samp, cr_samp = comp[1], comp[4], comp[7]
        chroma_map = {
            ((2, 2), (1, 1), (1, 1)): "4:2:0",
            ((2, 1), (1, 1), (1, 1)): "4:2:2",
            ((1, 1), (1, 1), (1, 1)): "4:4:4",
            ((1, 2), (1, 1), (1, 1)): "4:4:0",
        }
        key = (
            (y_samp >> 4, y_samp & 0x0F),
            (cb_samp >> 4, cb_samp & 0x0F),
            (cr_samp >> 4, cr_samp & 0x0F),
        )
        return chroma_map.get(key)

    @staticmethod
    def _parse_jpeg(data: bytes) -> dict:
        if not data.startswith(b"\xff\xd8"):
            return {}

        offset = 2
        data_len = len(data)
        sof_markers = {
            0xC0,
            0xC1,
            0xC2,
            0xC3,
            0xC5,
            0xC6,
            0xC7,
            0xC9,
            0xCA,
            0xCB,
            0xCD,
            0xCE,
            0xCF,
        }

        while offset < data_len - 1:
            if data[offset] != 0xFF:
                offset += 1
                continue

            marker = data[offset + 1]
            if marker in {0xD8, 0xD9}:  # SOI, EOI
                offset += 2
                continue

            if offset + 4 > data_len:
                break

            length = struct.unpack(">H", data[offset + 2 : offset + 4])[0]
            if marker in sof_markers:
                if offset + 10 > data_len:
                    break
                precision, h, w, num_comp = struct.unpack(
                    ">BHHB", data[offset + 4 : offset + 10]
                )
                meta = {
                    "format": "JPEG",
                    "size": (w, h),
                    "bit_depth": precision,
                    "mode": "L" if num_comp == 1 else "RGB",
                }

                if num_comp == 3 and offset + 19 <= data_len:
                    chroma = Exif._parse_jpeg_chroma(data[offset + 10 : offset + 19])
                    if chroma:
                        meta["chroma"] = chroma
                return meta

            offset += 2 + length
        return {}

    @staticmethod
    def _parse_tiff(data: bytes) -> dict:
        if not (data.startswith(b"II\x2a\x00") or data.startswith(b"MM\x00\x2a")):
            return {}

        endian = "<" if data[:2] == b"II" else ">"
        ifd_offset = struct.unpack(f"{endian}I", data[4:8])[0]
        if ifd_offset + 2 > len(data):
            return {"format": "TIFF"}

        num_entries = struct.unpack(f"{endian}H", data[ifd_offset : ifd_offset + 2])[0]
        entry_offset = ifd_offset + 2
        tags = {}

        for _ in range(num_entries):
            if entry_offset + 12 > len(data):
                break
            tag, typ, count, val = struct.unpack(
                f"{endian}HHII", data[entry_offset : entry_offset + 12]
            )
            entry_offset += 12

            parsed_val = val
            if typ == 3:  # SHORT
                if count == 1:
                    val_bytes = struct.pack(f"{endian}I", val)
                    parsed_val = struct.unpack(f"{endian}H", val_bytes[:2])[0]
                elif count > 1 and val + 2 <= len(data):
                    parsed_val = struct.unpack(f"{endian}H", data[val : val + 2])[0]

            tags[tag] = parsed_val

        meta = {"format": "TIFF"}
        if 256 in tags and 257 in tags:
            meta["size"] = (tags[256], tags[257])
        if 258 in tags:
            meta["bit_depth"] = tags[258]
        if 262 in tags:
            meta["mode"] = (
                "RGB"
                if tags[262] in {2, 6}
                else ("L" if tags[262] in {0, 1} else UNKNOWN)
            )
        return meta

    @staticmethod
    def _parse_webp(data: bytes) -> dict:
        if not (data.startswith(b"RIFF") and data[8:12] == b"WEBP"):
            return {}

        chunk_type = data[12:16]
        if chunk_type == b"VP8 " and len(data) >= 30:
            w_raw, h_raw = struct.unpack("<HH", data[26:30])
            return {
                "format": "WEBP",
                "size": (w_raw & 0x3FFF, h_raw & 0x3FFF),
                "bit_depth": 8,
                "mode": "RGB",
                "chroma": "4:2:0",
            }
        if chunk_type == b"VP8L" and len(data) >= 25:
            b0, b1, b2, b3 = data[21:25]
            val = b0 | (b1 << 8) | (b2 << 16) | (b3 << 24)
            return {
                "format": "WEBP",
                "size": ((val & 0x3FFF) + 1, ((val >> 14) & 0x3FFF) + 1),
                "bit_depth": 8,
                "mode": "RGBA" if (val & 0x10000000) else "RGB",
            }
        if chunk_type == b"VP8X" and len(data) >= 30:
            has_alpha = bool(data[20] & 0x10)
            w = (data[24] | (data[25] << 8) | (data[26] << 16)) + 1
            h = (data[27] | (data[28] << 8) | (data[29] << 16)) + 1
            return {
                "format": "WEBP",
                "size": (w, h),
                "bit_depth": 8,
                "mode": "RGBA" if has_alpha else "RGB",
            }
        return {"format": "WEBP"}

    @staticmethod
    def _parse_heic(data: bytes) -> dict:
        if len(data) < 12 or data[4:8] != b"ftyp":
            return {}

        brand = data[8:12]
        if brand not in {b"heic", b"heix", b"hevc", b"hevx", b"mif1", b"msf1"}:
            return {}

        meta = {"format": "HEIC", "bit_depth": 8, "mode": "RGB"}
        ispe_idx = data.find(b"ispe")
        if ispe_idx != -1 and ispe_idx + 16 <= len(data):
            w, h = struct.unpack(">II", data[ispe_idx + 8 : ispe_idx + 16])
            meta["size"] = (w, h)
        return meta

    @staticmethod
    def parse_raw_header(data: bytes) -> dict:
        """Extract metadata directly from raw image header bytes.

        Supports HEIC, JPG, PNG, TIFF, and WEBP.

        Args:
            data: Raw header bytes (minimum 64 KB recommended)

        Returns:
            dict: Parsed header metadata (format, size, bit_depth, mode, chroma)
        """
        if not data:
            return {}

        parsers = (
            Exif._parse_png,
            Exif._parse_jpeg,
            Exif._parse_tiff,
            Exif._parse_webp,
            Exif._parse_heic,
        )
        for parser in parsers:
            meta = parser(data)
            if meta:
                return meta

        return {}
