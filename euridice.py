import sys
import os
import subprocess
import cv2
import img2pdf

def download_video(url, output_filename="video.mp4"):
    print("Downloading video with yt-dlp (forcing H.264 codec for compatibility)...")
    
    # Force h264 codec
    cmd = [
        "yt-dlp", 
        "-S", "vcodec:h264", 
        "-f", "bestvideo[ext=mp4]/bestvideo", 
        "-o", output_filename, 
        url
    ]
    subprocess.run(cmd, check=True)
    return output_filename

def extract_and_filter_frames(video_path, threshold_percent=0.01):
    print("Processing video frames in memory...")
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS)
    # Check 1 frame every 5 seconds
    frame_skip = int(fps * 5)

    saved_frames = []
    last_kept_gray = None

    count = 0
    success, frame = cap.read()

    while success:
        if count % frame_skip == 0:
            # Convert frame to grayscale for easier comparison
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if last_kept_gray is None:
                # Always keep the very first frame
                saved_frames.append(frame)
                last_kept_gray = gray
                print("Saved page 1")
            else:
                # Compare current frame to the last kept frame
                diff = cv2.absdiff(last_kept_gray, gray)
                
                # If a pixel changed by a value of 30 (out of 255), flag it as "changed"
                _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
                changed_pixels = cv2.countNonZero(thresh)
                total_pixels = gray.size
                
                # Calculate the percentage of the image that changed
                percent_changed = changed_pixels / total_pixels

                # If more than the threshold (default 1%) changed, it's a new page!
                if percent_changed > threshold_percent:
                    saved_frames.append(frame)
                    last_kept_gray = gray
                    print(f"Saved page {len(saved_frames)} (Difference: {percent_changed:.2%})")

        success, frame = cap.read()
        count += 1

    cap.release()
    return saved_frames

def save_to_pdf(frames, output_filename="score.pdf"):
    print(f"\nStitching {len(frames)} pages into a PDF using img2pdf...")
    if not frames:
        print("No frames were captured!")
        return

    image_bytes_list = []
    
    # Compress each frame into JPEG bytes in memory
    for f in frames:
        # cv2.imencode returns a tuple: (success_boolean, memory_buffer)
        success, buffer = cv2.imencode(".jpg", f)
        if success:
            image_bytes_list.append(buffer.tobytes())
        else:
            print("Warning: Failed to encode a frame.")

    # Write the in-memory images directly to a PDF file
    if image_bytes_list:
        with open(output_filename, "wb") as f_out:
            f_out.write(img2pdf.convert(image_bytes_list))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python euridice.py <youtube_url>")
        sys.exit(1)

    url = sys.argv[1]
    video_file = "temp_video.mp4"
    pdf_file = "score.pdf"

    try:
        download_video(url, video_file)
        # threshold_percent=0.01 means "if 1% of the screen changes, capture it"
        frames = extract_and_filter_frames(video_file, threshold_percent=0.01)
        save_to_pdf(frames, pdf_file)
        print(f"Done! Score saved beautifully as {pdf_file}")
    finally:
        # Always clean up the video file, even if the script crashes
        if os.path.exists(video_file):
            os.remove(video_file)
            print("Cleaned up temporary video.")
