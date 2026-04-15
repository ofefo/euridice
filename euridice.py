import sys
import os
import subprocess
import cv2
import img2pdf
import re

def get_video_title(url):
    print("Fetching video title...")
    try:
        # Ask yt-dlp to just print the title of the video
        result = subprocess.run(
            ["yt-dlp", "--print", "title", url],
            capture_output=True, text=True, check=True
        )
        title = result.stdout.strip()
        
        # Strip out characters that are illegal in file paths (\ / * ? " < > | :)
        clean_title = re.sub(r'[\\/*?:"<>|]', "", title)
        
        # NEW: Replace all spaces with underscores
        clean_title = clean_title.replace(" ", "_")
        
        # Fallback to "score" just in case the title was entirely emojis/illegal characters
        return clean_title if clean_title else "score"
    except subprocess.CalledProcessError:
        print("Warning: Could not fetch title, defaulting to 'score'")
        return "score"

def download_video(url, output_filename="video.mp4"):
    print("Downloading video with yt-dlp (forcing H.264 codec for compatibility)...")
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
    frame_skip = int(fps * 2) # skip frames distant less than 2 seconds 

    saved_frames = []
    last_kept_gray = None

    count = 0
    success, frame = cap.read()

    while success:
        if count % frame_skip == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if last_kept_gray is None:
                saved_frames.append(frame)
                last_kept_gray = gray
                print("Saved page 1")
            else:
                diff = cv2.absdiff(last_kept_gray, gray)
                _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
                
                changed_pixels = cv2.countNonZero(thresh)
                total_pixels = gray.size
                percent_changed = changed_pixels / total_pixels

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
    
    for f in frames:
        success, buffer = cv2.imencode(".jpg", f)
        if success:
            image_bytes_list.append(buffer.tobytes())
        else:
            print("Warning: Failed to encode a frame.")

    if image_bytes_list:
        with open(output_filename, "wb") as f_out:
            f_out.write(img2pdf.convert(image_bytes_list))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python euridice.py <youtube_url>")
        sys.exit(1)

    url = sys.argv[1]
    video_file = "temp_video.mp4"
    
    # 1. Fetch and clean the title dynamically
    video_title = get_video_title(url)
    pdf_file = f"{video_title}.pdf"

    try:
        # 2. Download to a temporary file
        download_video(url, video_file)
        
        # 3. Process frames in memory
        frames = extract_and_filter_frames(video_file, threshold_percent=0.01)
        
        # 4. Save to PDF using the dynamic title
        save_to_pdf(frames, pdf_file)
        print(f"Done! Score saved beautifully as '{pdf_file}'")
        
    finally:
        # 5. Always clean up
        if os.path.exists(video_file):
            os.remove(video_file)
            print("Cleaned up temporary video.")
