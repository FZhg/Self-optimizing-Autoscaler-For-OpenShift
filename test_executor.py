from unittest import TestCase
from executor import Executor


class TestExecutor(TestCase):
    def test_horizontal_scale(self):
        Executor.horizontal_scale('acmeair-bookingservice', 9, 3)

    def test_scale_jvm_heap_size(self):
        Executor.scale_jvm_heap_size('acmeair-mainservice', 512, 256)


