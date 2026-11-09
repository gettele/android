#!/usr/bin/env python3
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tl_index


class OptionalFieldsTest(unittest.TestCase):
    def test_numeric_profile_masks(self):
        body = '''
        public void serializeToStream(OutputSerializedData stream) {
            if (hasFlag(flags, 1)) {
                stream.writeString(first_name);
            }
            if (hasFlag(flags, 2)) {
                stream.writeString(last_name);
            }
            if (hasFlag(flags, 4)) {
                stream.writeString(about);
            }
        }
        '''
        self.assertEqual(tl_index.optional_fields(body), {
            'first_name': 1, 'last_name': 2, 'about': 4,
        })

    def test_symbolic_flags_are_bit_positions(self):
        body = '''
        public void serializeToStream(OutputSerializedData stream) {
            flags = setFlag(flags, FLAG_0, fallback);
            if (hasFlag(flags, FLAG_2)) {
                stream.writeString(about);
            }
            if (hasFlag(flags, FLAG_31)) {
                stream.writeInt64(id);
            }
        }
        '''
        self.assertEqual(tl_index.optional_fields(body), {
            'fallback': 1, 'about': 4, 'id': 2147483648,
        })

    def test_read_and_guarded_masks(self):
        body = '''
        public void serializeToStream(OutputSerializedData stream) {
            if (photo != null) flags |= 0x20;
            flags = setFlag(flags, 8, enabled);
        }
        public void readParams(InputSerializedData stream, boolean exception) {
            if (hasFlag(flags, 16)) {
                name = stream.readString(exception);
            }
            active = hasFlag(flags, FLAG_1);
        }
        '''
        self.assertEqual(tl_index.optional_fields(body), {
            'photo': 32, 'enabled': 8, 'name': 16, 'active': 2,
        })

    def test_required_fields_have_no_mask(self):
        body = '''
        public void serializeToStream(OutputSerializedData stream) {
            stream.writeString(name);
        }
        '''
        self.assertEqual(tl_index.optional_fields(body), {})


if __name__ == '__main__':
    unittest.main()
