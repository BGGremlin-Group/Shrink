#!/data/data/com.termux/files/usr/bin/python  
import os, sys, shutil, subprocess  
from pathlib import Path  
  
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".3gp", ".m4v"}  
  
def clear():  
    os.system("clear")  
  
def pause(msg="Press Enter to continue..."):  
    input(msg)  
  
def run(cmd, check=True, capture=True):  
    p = subprocess.run(cmd, text=True,  
                       stdout=subprocess.PIPE if capture else None,  
                       stderr=subprocess.PIPE if capture else None)  
    if check and p.returncode != 0:  
        raise RuntimeError(  
            f"Command failed: {' '.join(cmd)}\n\nSTDOUT:\n{p.stdout}\n\nSTDERR:\n{p.stderr}"  
        )  
    return p  
  
def ffprobe_duration_seconds(infile: Path) -> float:  
    out = run([  
        "ffprobe", "-v", "error",  
        "-show_entries", "format=duration",  
        "-of", "default=nw=1:nk=1",  
        str(infile)  
    ]).stdout.strip()  
    return float(out)  
  
def human_bytes(n: int) -> str:  
    b = float(n)  
    units = ["B", "KB", "MB", "GB", "TB"]  
    i = 0  
    while b >= 1024 and i < len(units) - 1:  
        b /= 1024.0  
        i += 1  
    return f"{b:.2f} {units[i]}"  
  
def is_video(p: Path) -> bool:  
    return p.is_file() and p.suffix.lower() in VIDEO_EXTS  
  
def safe_listdir(path: Path):  
    try:  
        items = list(path.iterdir())  
    except Exception:  
        return [], []  
    dirs = sorted([x for x in items if x.is_dir()], key=lambda x: x.name.lower())  
    files = sorted([x for x in items if is_video(x)], key=lambda x: x.name.lower())  
    return dirs, files  
  
def pick_int_menu(title, entries, default_idx=0):  
    while True:  
        clear()  
        print(title)  
        print("=" * len(title))  
        for i, (label, _) in enumerate(entries, 1):  
            print(f"{i}) {label}")  
        print("0) Use default")  
        s = input(f"Select (default {default_idx+1}): ").strip()  
        if s == "0" or s == "":  
            return entries[default_idx][1]  
        if s.isdigit():  
            idx = int(s) - 1  
            if 0 <= idx < len(entries):  
                return entries[idx][1]  
        print("Invalid choice.")  
        pause()  
  
def ask_float(prompt, default=9.0, min_val=0.5):  
    while True:  
        s = input(f"{prompt} [{default}]: ").strip()  
        if not s:  
            v = float(default)  
        else:  
            try:  
                v = float(s)  
            except Exception:  
                print("Please enter a number.")  
                continue  
        if v < min_val:  
            print(f"Must be >= {min_val}")  
            continue  
        return v  
  
def browse_for_video(start_dir: Path) -> Path | None:  
    current = start_dir  
    while True:  
        dirs, vids = safe_listdir(current)  
  
        clear()  
        print("Pick a video file")  
        print("=================")  
        print(f"Current folder: {current}\n")  
        print("[..] up   [~] home   [S] shared   [R] refresh   [Q] quit\n")  
  
        print("Folders:")  
        if not dirs:  
            print("  (none)")  
        else:  
            for i, d in enumerate(dirs, 1):  
                print(f"  D{i:>2}) {d.name}/")  
  
        print("\nVideos:")  
        if not vids:  
            print("  (none)")  
        else:  
            for i, f in enumerate(vids, 1):  
                try:  
                    size = human_bytes(f.stat().st_size)  
                except Exception:  
                    size = "?"  
                print(f"  V{i:>2}) {f.name}   ({size})")  
  
        cmd = input("\nCommand (D#, V#, .., ~, S, R, Q): ").strip()  
        if not cmd:  
            continue  
        c = cmd.lower()  
  
        if c == "q":  
            return None  
        if c == "r":  
            continue  
        if c == "~":  
            current = Path.home()  
            continue  
        if c == "s":  
            current = Path.home() / "storage" / "shared"  
            continue  
        if cmd == "..":  
            parent = current.parent  
            if parent != current:  
                current = parent  
            continue  
  
        if len(cmd) >= 2 and cmd[0].lower() == "d" and cmd[1:].isdigit():  
            idx = int(cmd[1:]) - 1  
            if 0 <= idx < len(dirs):  
                current = dirs[idx]  
            else:  
                print("No such folder number.")  
                pause()  
            continue  
  
        if len(cmd) >= 2 and cmd[0].lower() == "v" and cmd[1:].isdigit():  
            idx = int(cmd[1:]) - 1  
            if 0 <= idx < len(vids):  
                return vids[idx]  
            print("No such video number.")  
            pause()  
            continue  
  
        print("Unknown command.")  
        pause()  
  
def compute_video_kbps(target_mb, duration_s, audio_kbps):  
    target_bits = target_mb * 1024 * 1024 * 8  
    audio_bits = audio_kbps * 1000 * duration_s  
    video_bits = target_bits - audio_bits  
    if video_bits <= 0:  
        return -1  
    return int((video_bits / duration_s) / 1000)  
  
def encode_two_pass(infile, outfile, v_kbps, audio_kbps, max_height):  
    vf_args = []  
    if max_height:  
        vf_args = ["-vf", f"scale=-2:{max_height}"]  
  
    passlog = str(outfile) + ".passlog"  
  
    cmd1 = [  
        "ffmpeg", "-y", "-i", str(infile),  
        *vf_args,  
        "-c:v", "libx264",  
        "-b:v", f"{v_kbps}k",  
        "-maxrate", f"{v_kbps}k",  
        "-bufsize", f"{v_kbps*2}k",  
        "-pass", "1", "-passlogfile", passlog,  
        "-preset", "veryfast",  
        "-an",  
        "-f", "mp4", "/dev/null"  
    ]  
  
    cmd2 = [  
        "ffmpeg", "-y", "-i", str(infile),  
        *vf_args,  
        "-c:v", "libx264",  
        "-b:v", f"{v_kbps}k",  
        "-maxrate", f"{v_kbps}k",  
        "-bufsize", f"{v_kbps*2}k",  
        "-pass", "2", "-passlogfile", passlog,  
        "-preset", "veryfast",  
        "-movflags", "+faststart",  
        "-c:a", "aac", "-b:a", f"{audio_kbps}k",  
        str(outfile)  
    ]  
  
    try:  
        print("\nPass 1/2…")  
        subprocess.run(cmd1, check=True)  
        print("Pass 2/2…")  
        subprocess.run(cmd2, check=True)  
    finally:  
        for ext in ("", ".mbtree"):  
            try:  
                Path(passlog + ext).unlink(missing_ok=True)  
            except Exception:  
                pass  
  
def main():  
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:  
        print("ffmpeg/ffprobe not found. Install with: pkg install ffmpeg")  
        sys.exit(1)  
  
    shared = Path.home() / "storage" / "shared"  
    start_dir = shared if shared.is_dir() else Path.home()  
  
    infile = browse_for_video(start_dir)  
    if infile is None:  
        clear()  
        print("Cancelled.")  
        return  
  
    clear()  
    in_size = infile.stat().st_size  
    print("Target size")  
    print("===========")  
    print(f"Selected: {infile}")  
    print(f"Current : {human_bytes(in_size)}\n")  
  
    target_mb = ask_float("Enter target size in MB", default=9.0, min_val=0.5)  
  
    audio_kbps = pick_int_menu(  
        "Audio bitrate (kbps)",  
        [("48 kbps (smallest, ok for voice)", 48),  
         ("64 kbps (small, decent)", 64),  
         ("96 kbps (default, good)", 96),  
         ("128 kbps (better, larger)", 128)],  
        default_idx=2  
    )  
  
    max_height = pick_int_menu(  
        "Downscale? (max height)",  
        [("None (keep original)", 0),  
         ("720p max height", 720),  
         ("480p max height", 480),  
         ("360p max height", 360)],  
        default_idx=0  
    )  
    if max_height == 0:  
        max_height = None  
  
    out_choice = pick_int_menu(  
        "Output location",  
        [("Same folder as input", 1),  
         ("Shared storage /Movies (if exists)", 2),  
         ("Termux home (~)", 3)],  
        default_idx=0  
    )  
  
    if out_choice == 1:  
        out_dir = infile.parent  
    elif out_choice == 2:  
        movies = shared / "Movies"  
        out_dir = movies if movies.is_dir() else shared  
    else:  
        out_dir = Path.home()  
  
    mb_tag = f"{target_mb:.2f}".rstrip("0").rstrip(".")  
    outfile = out_dir / f"{infile.stem}_{mb_tag}mb.mp4"  
  
    clear()  
    dur = ffprobe_duration_seconds(infile)  
    v_kbps = compute_video_kbps(target_mb, dur, audio_kbps)  
    if v_kbps <= 0:  
        print("Target too small for chosen audio bitrate.")  
        print("Pick a larger target MB or lower audio bitrate (48/64).")  
        pause()  
        return  
  
    print("Plan")  
    print("====")  
    print(f"Input    : {infile}")  
    print(f"Output   : {outfile}")  
    print(f"Duration : {dur:.2f}s")  
    print(f"Target   : {target_mb} MB")  
    print(f"Audio    : {audio_kbps} kbps")  
    print(f"Video    : {v_kbps} kbps (computed)")  
    print(f"Scale    : {'none' if not max_height else f'max height {max_height}'}\n")  
  
    if input("Start encoding now? (y/N): ").strip().lower() != "y":  
        print("Cancelled.")  
        pause()  
        return  
  
    encode_two_pass(infile, outfile, v_kbps, audio_kbps, max_height)  
  
    clear()  
    if outfile.exists():  
        out_size = outfile.stat().st_size  
        out_mb = out_size / (1024 * 1024)  
        print("Done ✅")  
        print("=======")  
        print(f"Output: {outfile}")  
        print(f"Size  : {human_bytes(out_size)} ({out_mb:.2f} MB)")  
        if out_mb > target_mb:  
            print("\nSlightly over target can happen.")  
            print("Try one of:")  
            print("  • set target to 8.8 instead of 9")  
            print("  • choose audio 64 kbps")  
            print("  • choose 720p/480p downscale")  
    else:  
        print("Output not created.")  
    pause()  
  
if __name__ == "__main__":  
    main()
