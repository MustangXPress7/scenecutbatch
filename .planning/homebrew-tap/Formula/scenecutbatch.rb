class Scenecutbatch < Formula
  desc "Batch scene-cut detection that emits FCP7 XML importable by professional video editors"
  homepage "https://github.com/MustangXPress7/scenecutbatch"
  version "0.1.1"

  # macOS binaries are published as GitHub Release assets once a macOS build
  # job is added to .github/workflows/release.yml. Until then this formula is
  # a skeleton; update url + sha256 when the first macOS asset is published.
  if OS.mac?
    if Hardware::CPU.arm?
      url "https://github.com/MustangXPress7/scenecutbatch/releases/download/v0.1.1/scenecutbatch-0.1.1-macos-aarch64.app.zip"
      sha256 "REVISAR_AL_PUBLICAR"
    else
      url "https://github.com/MustangXPress7/scenecutbatch/releases/download/v0.1.1/scenecutbatch-0.1.1-macos-x86_64.app.zip"
      sha256 "REVISAR_AL_PUBLICAR"
    end
  end

  def install
    if OS.mac?
      app_dir = Dir["*.app"].first
      prefix.install app_dir
      bin.install_symlink "#{prefix}/#{File.basename(app_dir)}/Contents/MacOS/scenecutbatch"
    end
  end

  test do
    system "#{bin}/scenecutbatch", "--version"
  end
end
