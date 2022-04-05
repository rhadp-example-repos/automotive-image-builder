NAME=autosig-watchdog

srpm:
	rpmbuild -bs ${NAME}.spec --define "_topdir `pwd`"

local:
	rpmbuild -ba ${NAME}.spec --define "_topdir `pwd`"
