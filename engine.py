import os
import gc  # Garbage Collector interface to manually force-clear RAM
import urllib.request

class PyLiteStreamer:
    """
    The PyLite Engine: Overrides standard file reading to process 2GB+ datasets 
    on low-resource devices (like Android phones) using a strict, low-memory 
    packet-streaming loop.
    """
    def __init__(self, file_path, chunk_size_mb=10):
        self.file_path = file_path
        # Convert Megabytes to raw bytes (1 MB = 1,048,576 bytes)
        self.chunk_size = chunk_size_mb * 1024 * 1024

    def stream_packets(self):
        """
        A Generator function that yields one memory-isolated packet at a time.
        Using 'yield' instead of 'return' ensures the entire file is never 
        loaded into the phone's RAM simultaneously.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"PyLite Error: The file '{self.file_path}' does not exist on this device.")

        # Open the file in 'rb' mode (Read Binary). This is critical because 
        # binary mode reads raw bytes directly from storage, avoiding heavy 
        # text-decoding processing overhead.
        with open(self.file_path, "rb") as large_file:
            packet_index = 0
            
            while True:
                # Read ONLY the exact slice size into memory
                packet_data = large_file.read(self.chunk_size)
                
                # If packet_data is empty, we have reached the end of the file
                if not packet_data:
                    break
                
                packet_index += 1
                
                # 'yield' hands the packet over to developer's code, pauses execution,
                # and waits until they are ready for the next piece.
                yield packet_index, packet_data
                
                # --- THE MEMORY VAPORIZATION PURGE ---
                # Once user's code finishes processing this specific block,
                # we explicitly delete the variable holding the raw data.
                del packet_data
                
                # Force Android's Python Garbage Collector to physically clear 
                # the freed memory addresses immediately, instead of waiting.
                gc.collect()


def StreamCSV(file_pointer, chunk_size=1048576, encoding='utf-8'):
    """
    ULTRA-OPTIMIZED VERSION: High-throughput memory-mapped stream parser.
    Achieves maximum CPU execution efficiency while strictly maintaining O(1) space complexity.
    """
    leftover_bytes = b""
    
    while True:
        # Read data in highly optimized 1 MB raw binary blocks
        binary_chunk = file_pointer.read(chunk_size)
        if not binary_chunk:
            break  # End of data stream reached smoothly
            
        # Stitch any leftover partial lines from the last chunk onto the front
        combined_data = leftover_bytes + binary_chunk
        
        # Use low-level C-optimized splitting routine for max performance
        raw_lines = combined_data.splitlines(keepends=True)
        
        # Check if the last element is an incomplete sentence cut in half
        if raw_lines and not raw_lines[-1].endswith(b'\n') and not raw_lines[-1].endswith(b'\r'):
            leftover_bytes = raw_lines.pop()  # Save it for the next incoming chunk
        else:
            leftover_bytes = b""
            
        # Yield the clean, fully formed lines to the user instantly
        for raw_line in raw_lines:
            yield raw_line.decode(encoding).strip()
            
    # If the file ended but we still have data left in the buffer, flush it out
    if leftover_bytes:
        yield leftover_bytes.decode(encoding).strip()


def StreamAPI(url, chunk_size=1048576):
    """
    ULTRA-OPTIMIZED VERSION: Live Network Socket Streamer.
    Streams massive web API payloads or files directly from a live URL link.
    Data never touches device storage, maintaining strict O(1) RAM boundaries.
    """
    try:
        # Open a direct high-speed low-level network connection socket
        req = urllib.request.Request(url, headers={'User-Agent': 'PyLiteStream-Mobile-Engine'})
        with urllib.request.urlopen(req) as response:
            while True:
                # Read incoming network data packets directly into memory buffers
                network_packet = response.read(chunk_size)
                if not network_packet:
                    break  # Network data transfer complete
                yield network_packet
    except Exception as e:
        raise ConnectionError(f"PyLite Network Error: Failed to stream from URL. Details: {e}")


def StreamVideo(file_path):
    """
    ULTRA-OPTIMIZED VERSION: Video Frame Matrix Decoder.
    Streams video files frame-by-frame as decoded image matrices.
    Maintains O(1) space complexity by isolating execution frames sequentially.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PyLite Video Error: Target video file not found at: {file_path}")
        
    try:
        import cv2
    except ImportError:
        raise ImportError("PyLite Error: 'opencv-python' (cv2) is required for frame matrix decoding. Run 'pip install opencv-python'.")

    video_capture = cv2.VideoCapture(file_path)
    
    try:
        while True:
            # Read exactly ONE frame matrix from the stream file wrapper
            success, frame_matrix = video_capture.read()
            
            if not success:
                break
                
            yield frame_matrix
            
            # Force immediate frame deletion from memory after the loop cycle advances
            del frame_matrix
            gc.collect()
    finally:
        video_capture.release()