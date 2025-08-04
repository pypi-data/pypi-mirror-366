from inspect import signature
from multiprocessing.shared_memory import SharedMemory
from struct import calcsize, pack, unpack
from typing import Optional, Self

from posix_ipc import Semaphore, O_CREX

_SHM_SUPPORTS_TRACK = 'track' in signature(SharedMemory).parameters

class SharedMemoryPipe:
    HEADER_FMT = 'I B 3x'  # uint32 size, uint8 eof, 3-byte pad
    HEADER_SIZE = calcsize(HEADER_FMT)

    def __init__(
        self,
        name: Optional[str] = None,
        *,
        max_slots: int = 64,
        slot_size: int = 4096,
    ):

        self.max_slots = max_slots
        self.slot_size = slot_size
        self.chunk_size = slot_size
        self.is_writer = name is None
        self._closed = False

        self.local_index = 0



        shm_kwargs = {}
        if _SHM_SUPPORTS_TRACK:
            shm_kwargs['track'] = False

        if self.is_writer:
            shm_kwargs["create"] = True
            shm_kwargs["size"] = self.chunk_size * self.max_slots
            self.shm = SharedMemory(**shm_kwargs)

            self._items_sem_name = self.shm.name + "_items"
            self._slots_sem_name = self.shm.name + "_slots"
            self.items = Semaphore(self._items_sem_name, flags=O_CREX, initial_value=0)
            self.slots = Semaphore(self._slots_sem_name, flags=O_CREX, initial_value=self.max_slots)
        else:
            shm_kwargs["name"] = name
            self._items_sem_name = name + "_items"
            self._slots_sem_name = name + "_slots"
            self.shm = SharedMemory(**shm_kwargs)
            self.items = Semaphore(self._items_sem_name)
            self.slots = Semaphore(self._slots_sem_name)

    @property
    def name(self):
        return self.shm.name

    def _write_slot(self, data: bytes, eof: bool):
        self.slots.acquire()

        slot_index = self.local_index % self.max_slots
        offset = slot_index * self.chunk_size

        header = pack(self.HEADER_FMT, len(data), int(eof))
        self.shm.buf[offset:offset + self.HEADER_SIZE] = header
        self.shm.buf[offset + self.HEADER_SIZE:offset + self.HEADER_SIZE + len(data)] = data

        self.local_index += 1
        self.items.release()

    def write(self, data: bytes, /, *, close: bool = False):
        max_payload = self.chunk_size - self.HEADER_SIZE
        total_chunks = (len(data) + max_payload - 1) // max_payload

        for i in range(total_chunks):
            chunk = data[i * max_payload:(i + 1) * max_payload]
            eof = close and (i == total_chunks - 1)
            self._write_slot(chunk, eof=eof)

    def read(self) -> Optional[bytes]:
        self.items.acquire()

        slot_index = self.local_index % self.max_slots
        offset = slot_index * self.chunk_size

        header = self.shm.buf[offset:offset + self.HEADER_SIZE]
        size, is_eof = unpack(self.HEADER_FMT, header)

        data = bytes(self.shm.buf[offset + self.HEADER_SIZE:offset + self.HEADER_SIZE + size])
        self.local_index += 1

        self.slots.release()
        return None if is_eof else data

    def reader(self) -> Self:
        if not self.is_writer:
            raise RuntimeError("Only writer can spawn reader")
        return SharedMemoryPipe(
            name=self.name,
            max_slots=self.max_slots,
            slot_size=self.slot_size,
        )

    def close(self):
        if self._closed:
            return
        self._closed = True

        if self.is_writer:
            self._write_slot(b'', eof=True)
            self.shm.close()
        else:
            self.shm.close()
            self.shm.unlink()

        self.shm = None  # Prevent reuse

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __getstate__(self):
        if self.is_writer:
            raise RuntimeError("Writer cannot be pickled")
        return {
            'name': self.name,
            'max_slots': self.max_slots,
            'slot_size': self.slot_size,
        }

    def __setstate__(self, state):
        self.__init__(**state)
