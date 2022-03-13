#! /bin/sh
mkdir -p dist
awk '
BEGIN{
    lim = 78;
    lcnt = 1;
}
NR == FNR && !/^# %%/ {
    pfn = FILENAME
    if (length($0) > lim && index($0, "\"doc_url\":") == 0) {
        print "too long\t" FILENAME "\t" FNR > "/dev/stderr";
    }
    m = m "\n" $0;
    if (length($0)>0) {
        lcnt++;
    }
    next;
}
FNR == 1 {
    flag = 0
    if (length(pfn) > 0){
        print pfn "\t" lcnt > "/dev/stderr";
    }
    pfn = FILENAME;
    lcnt = 1;
}
/^def test\(\):$/ {
    flag = 1
}
flag == 0 && !/^# %%/ && !/^import/ && !/^from prefs import/ {
    if (length($0) > lim) {
        print "too long\t"FILENAME "\t" FNR  > "/dev/stderr";
    }
    l = l "\n" $0;
    if (length($0)>0) {
        lcnt++;
    }
}
END {
    print pfn "\t" lcnt  > "/dev/stderr";
    sub("# _lib_", l, m);
    gsub("\n{3,}", "\n\n", m);
    sub("^\n", "", m);
    print m;
}
' \
src/E2MN.py \
src/prefs.py \
src/tree.py \
src/graph.py \
src/shader.py \
src/layout.py > dist/Expression2MathNodes.py
wc dist/Expression2MathNodes.py