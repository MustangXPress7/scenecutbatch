Name: scenecutbatch
Version: 0.1.0
Release: 1%{?dist}
Summary: Batch scene-cut detection for Adobe Premiere Pro
License: Apache-2.0
URL: https://github.com/MustangXPress7/scenecutbatch
Source0: %{name}-%{version}.tar.gz
BuildArch: noarch

Requires: python3 >= 3.10
Requires: python3-pip
Requires: ffmpeg

%description
SceneCutBatch detects hard scene cuts across folders of video clips using
PySceneDetect and emits Premiere-importable FCP7 XML files with virtual
subclips referencing the original media (no duplication).

%prep
%setup -q

%build
# No build step required for Python package

%install
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/lib/python3.10/dist-packages/scenecutbatch

cat > %{buildroot}/usr/bin/scenecutbatch <<'EOF'
#!/usr/bin/env python3
import sys
from scenecutbatch.cli import main

if __name__ == "__main__":
    sys.exit(main())
EOF
chmod 0755 %{buildroot}/usr/bin/scenecutbatch

cp -r src/scenecutbatch/* %{buildroot}/usr/lib/python3.10/dist-packages/scenecutbatch/
find %{buildroot}/usr/lib -name '__pycache__' -type d -prune -exec rm -rf {} +

%files
%license LICENSE
%doc README.md
/usr/bin/scenecutbatch
/usr/lib/python3.10/dist-packages/scenecutbatch

%changelog
* Thu Oct 22 2026 Scene Cut Batch <maintainer@scenecutbatch.com> - 0.1.0-1
- Initial RPM package for SceneCutBatch
