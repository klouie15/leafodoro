{ pkgs }: {
  deps = [
    pkgs.ffmpeg
    (pkgs.ffmpeg.bin)  # Add FFmpeg
    (pkgs.libopus)     # Add libopus
  ];
  env = {
  };
}