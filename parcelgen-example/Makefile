SRC=$(wildcard parcelables/*.json)
YAML=$(wildcard parcelables/*.yaml)
CONF=parcelgen.yaml
DIR=src/$(shell grep 'default_package' $(CONF) | sed 's/^[ ]*default_package: //' | sed 's/\./\//g')
DEST=$(patsubst parcelables/%.json,$(DIR)/_%.java,$(SRC))
DEST_YAML=$(patsubst parcelables/%.yaml,$(DIR)/_%.java,$(YAML))

all: $(DEST) $(DEST_YAML)

yaml: $(DEST_YAML)

$(DEST) : $(SRC) $(CONF) | $(DIR)
	python ../parcelgen.py $< $@

$(DEST_YAML) : $(YAML) $(CONF) | $(DIR)
	python ../parcelgen.py -c $(CONF) $< $@

$(DIR):
	mkdir -p $(DIR)

clean:
	rm -f $(DEST)