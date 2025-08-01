lib: python_pkgs:
let
  pname = "types-pyRFC3339";
  version = "2.0.1.20241107";
in lib.buildPythonPackage {
  inherit pname version;
  src = lib.fetchPypi {
    inherit pname version;
    hash = "sha256-D4Q4D8k8HGX9RfBq/Frg75CHRBF4CGNSVJDHkk2FvF0=";
  };
  pyproject = true;
  build-system = [ python_pkgs.setuptools ];
}
