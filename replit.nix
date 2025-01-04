
{ pkgs }: {
  deps = [
    pkgs.bash
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.django
    pkgs.postgresql
    pkgs.postgresql.lib
    pkgs.python311Packages.psycopg2
    pkgs.python311Packages.pillow
  ];
}
