#
# Builds every generated bundle in src/generated/bundles.txt with Apple's
# DictionaryDevelopmentKit and (optionally) installs them all.
#
# Run `python scripts/build_dict.py --all` first to populate src/generated/.
#

.PHONY: all install clean

DICT_DEV_KIT_OBJ_DIR = /Applications/XcodeAdditionalTools/Utilities/DictionaryDevelopmentKit
DICT_BUILD_TOOL_DIR  = $(DICT_DEV_KIT_OBJ_DIR)/bin
BUILD_DICT_XML        = $(DICT_BUILD_TOOL_DIR)/build_dict.sh

MIN_OS_VERSION   = 10.6
export MACOSX_DEPLOYMENT_TARGET=$(MIN_OS_VERSION)

GEN_DIR      = src/generated
OBJECTS_DIR  = src/objects
CSS_PATH     = src/shared/Nordic.css
INSTALL_DIR  = $(HOME)/Library/Dictionaries

# build_dict.sh wipes its objects/ directory on every invocation, so each
# bundle must be built AND copied out before moving on to the next one —
# a separate build-everything-then-install-everything pass would only leave
# the last bundle standing.
all:
	@if [ ! -f "$(GEN_DIR)/bundles.txt" ]; then \
		echo "No bundles found. Run: python scripts/build_dict.py --all"; exit 1; \
	fi
	@mkdir -p $(OBJECTS_DIR) built
	@while read -r NAME; do \
		[ -z "$$NAME" ] && continue; \
		echo "Building $$NAME..."; \
		(cd $(OBJECTS_DIR) && "$(BUILD_DICT_XML)" "$$NAME" "../generated/$$NAME.xml" "../shared/Nordic.css" "../generated/$$NAME.plist"); \
		rm -rf "built/$$NAME.dictionary"; \
		cp -R "$(OBJECTS_DIR)/objects/$$NAME.dictionary" "built/"; \
	done < "$(GEN_DIR)/bundles.txt"

install: all
	@mkdir -p "$(INSTALL_DIR)"
	@while read -r NAME; do \
		[ -z "$$NAME" ] && continue; \
		echo "Installing $$NAME.dictionary..."; \
		rm -rf "$(INSTALL_DIR)/$$NAME.dictionary"; \
		cp -R "built/$$NAME.dictionary" "$(INSTALL_DIR)/"; \
	done < "$(GEN_DIR)/bundles.txt"
	@echo "Installed. Open Dictionary.app Settings and enable the ones you want."

clean:
	$(RM) -rf $(OBJECTS_DIR) $(GEN_DIR) built
