let nixpkgs = import <nixpkgs> {};
in
nixpkgs.stdenv.mkDerivation {
	name = "Arachomb";
	buildInputs=[ ];
}
