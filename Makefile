CHANGELOG	:= CHANGELOG.md
SOURCES		:= mergeconf/*.py
VERSION		:= $(shell git describe | sed 's/^v//')
PACKAGES	:= dist/mergeconf-$(VERSION)-py3-none-any.whl dist/mergeconf-$(VERSION).tar.gz

all: $(PACKAGES)

.PHONY: $(CHANGELOG)
$(CHANGELOG):
	@printf "# Changelog\n\n" > $(CHANGELOG)
	@format='## %(tag) (%(*committerdate:format:%Y-%m-%d)) %(subject)%0a%0a%(body)' ; \
        tags=`git for-each-ref refs/tags \
                 --format='%(objecttype) %(refname:lstrip=2)' \
                | awk '$$1 == "tag" { print $2 }'`; \
        git tag --list --sort=-\*committerdate \
                --format="$$format" $$tags \
	>> $(CHANGELOG)

$(PACKAGES): $(SOURCES)
	@sed -i 's/\(version =\) .*/\1 '$(VERSION)'/' setup.cfg
	@python3 -m build

upload-test: $(PACKAGES)
	@python3 -m twine upload --repository testpypi dist/mergeconf-$(VERSION){.tar.gz,-none-any.whl}

upload: $(PACKAGES)
	@python3 -m twine upload --repository pypi dist/mergeconf-$(VERSION){.tar.gz,-none-any.whl}
	
