def intersect(x;y):
  ( (x|unique) + (y|unique) | sort) as $sorted
  | reduce range(1; $sorted|length) as $i
      ([];
       if $sorted[$i] == $sorted[$i-1] then . + [$sorted[$i]] else . end) ;

def difference($a; $b):
    ($a | unique) - $b;

{
  cs9: {
    common: ((intersect($aarch64;$x86_64)) | sort_by(ascii_downcase)),
    arch: {
      x86_64: (($x86_64 - $aarch64) | sort_by(ascii_downcase)),
      aarch64: (($aarch64 - $x86_64) | sort_by(ascii_downcase))
    }
  }
}
