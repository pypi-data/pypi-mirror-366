lib: python_pkgs:
let
  pname = "types_jsonschema";
  version = "4.23.0.20250516";
in lib.buildPythonPackage {
  inherit pname version;
  src = lib.fetchPypi {
    inherit pname version;
    hash = "sha256-ms4J2dNcQ5CnJRzNfYM7kszBidJNGzR/JiEq/ONhEX4=";
  };
  pyproject = true;
  build-system = [ python_pkgs.setuptools ];
  dependencies = with python_pkgs; [ referencing ];
}
