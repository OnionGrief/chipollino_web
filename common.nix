{
  pkgs ? import (builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/89570f24e97e614aa34aa9ab1c927b6578a43775.tar.gz";
    sha256 = "sha256:0jfrm4wdjfg8d45b4gnxrcwa8kzclv9qisbv68v19d6fd4mdgk0h";
  }) { },
}:

let
  refal5 = pkgs.stdenv.mkDerivation {
    pname = "refal5";
    version = "081222";

    src = pkgs.fetchzip {
      url = "http://www.botik.ru/pub/local/scp/refal5/ref5_081222.zip";
      sha256 = "sha256:0mgq8da64srvw1b09yyaqbp072v6q3kvwpgn7rba097b88m2z06f";
      stripRoot = false;
    };

    nativeBuildInputs = [ pkgs.unzip ];

    buildPhase = ''
      make -f makefile.lin C_FLAGS="-c -DFOR_OS_LINUX -Wall -funsigned-char -std=gnu89"
    '';

    enableParallelBuilding = false;

    installPhase = ''
      mkdir -p $out/bin
      cp refc refgo reftr $out/bin/
    '';
  };

  chipollinoSrc = pkgs.fetchFromGitHub {
    owner = "OnionGrief";
    repo = "Chipollino";
    rev = "cdcaf86cc03b0e8c7415ba95a6704ddd2bcdd40d";
    sha256 = "sha256:1aaa3qqqyj16xn82dg3pf6r8yldm2vsbkhapys99ghzhx6vhj1hh";
  };

  configSrc = pkgs.fetchFromGitHub {
    owner = "OnionGrief";
    repo = "Automatic-Chipollino-Update";
    rev = "1e3d5715918eb90fb8c82e366a995b165d90c8b6";
    sha256 = "sha256:1gyyn6ylavbwm31cxac9srhg57868s0ywpnjffn49lb6hwmpzz7q";
  };

  lexySrc = pkgs.fetchzip {
    url = "https://lexy.foonathan.net/download/lexy-src.zip";
    sha256 = "sha256:1hi5n3k26z8zpslpii8lj4slmyvv9kg7w17nbx1gwzvw56wi1822";
    stripRoot = false;
  };

  chipollino = pkgs.stdenv.mkDerivation {
    pname = "chipollino";
    version = "0.1.0";
    src = chipollinoSrc;

    nativeBuildInputs = [
      pkgs.cmake
      pkgs.gnumake
      refal5
    ];

    postPatch = ''
      sed -i \
        -e '/add_subdirectory(apps\/UnitTestsApp)/d' \
        -e '/add_subdirectory(apps\/IntegrationTestsApp)/d' \
        -e '/add_subdirectory(apps\/MetamorphicTestsApp)/d' \
        CMakeLists.txt
    '';

    configurePhase = ''
      cmake -S . -B build \
        -DFETCHCONTENT_SOURCE_DIR_LEXY=${lexySrc}
    '';

    buildPhase = ''
      cmake --build build

      pushd refal
      chmod +x compile.sh
      PATH="${refal5}/bin:$PATH" ./compile.sh
      popd
    '';

    installPhase = ''
      mkdir -p $out
      cp -r . $out/
    '';
  };

  pythonEnv = pkgs.python312.withPackages (
    ps: with ps; [
      django
      graphviz
      latex2mathml
      gunicorn
      dot2tex
      pydot
      pyyaml
    ]
  );

  tex = pkgs.texlive.combine {
    inherit (pkgs.texlive)
      scheme-medium
      collection-latexextra
      collection-fontsextra
      collection-mathscience
      collection-langcyrillic
      dvisvgm
      ;
  };

  runtimePackages = [
    pythonEnv
    pkgs.graphviz
    tex
    refal5
    chipollino
  ];
in
{
  inherit
    pkgs
    refal5
    chipollino
    configSrc
    pythonEnv
    tex
    runtimePackages
    ;
}
