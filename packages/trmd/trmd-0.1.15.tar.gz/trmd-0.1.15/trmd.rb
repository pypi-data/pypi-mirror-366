class Trmd < Formula
  include Language::Python::Virtualenv

  desc "Translate Markdown using OpenAI"
  homepage "https://github.com/rioriost/homebrew-trmd/"
  url "https://files.pythonhosted.org/packages/07/ce/267bc19880da2400a57ffbe54bafdd77fc55765110488963bda2c27e0c0f/trmd-0.1.14.tar.gz"
  sha256 "31d0728fd7fa10732bd16e45663dea8fa7d04b3ae416f5cac02a773bf81ef88c"
  license "MIT"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "openai"
  end

  test do
    system "#{bin}/trmd", "--help"
  end
end
