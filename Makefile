.PHONY: \
	create_stack_package \
	create_app_package \
	package_version \
	install_app_package \
	install_stack_package \
	install_remotes \
	update_slce_extra \
	generate_pkg_slt \
	generate_pkg_slt_common \
	upload_app_package \
	upload_stack_package \
	remove_matter_packages \
	remove_all_packages \
	update_version
	enable_editable \
	disable_editable \
	editable_status \
	comment_revision_mode \
	uncomment_revision_mode \
	update_matter_version

RESOLVED_MATTER_VERSION := $(shell python3 slc/script/generate_pkg_slt.py --version-only)

# Allow override via environment: if PACKAGE_VERSION is exported it wins; otherwise read the file.
PACKAGE_VERSION := $(RESOLVED_MATTER_VERSION)
ifeq ($(strip $(SL_PRERELEASE_NUMBER)),)
$(info Using PACKAGE_VERSION from $(PACKAGE_VERSION_FILE): $(PACKAGE_VERSION))
else
SL_PRERELEASE_FILE := packages/.prerelease
SL_PRERELEASE := $(shell cat $(SL_PRERELEASE_FILE))
PACKAGE_VERSION := $(PACKAGE_VERSION)-$(SL_PRERELEASE).$(SL_PRERELEASE_NUMBER)
$(info Using PACKAGE_VERSION with pre-release: $(PACKAGE_VERSION))
endif
PACKAGE_REFERENCE := matter/$(PACKAGE_VERSION)@silabs

# ---------------------------------------------------------------------------
# Editable package helpers (developer convenience)
# ---------------------------------------------------------------------------

enable_editable: ## Put the local Matter package into Conan editable mode
	@echo "Enabling editable mode for $(PACKAGE_REFERENCE)"
	conan editable add . --name matter --version $(PACKAGE_VERSION) || { echo 'Failed to enable editable mode'; exit 1; }
	@echo "Editable mode ENABLED for $(PACKAGE_REFERENCE)"

disable_editable: ## Remove the local Matter package from Conan editable mode
	@echo "Disabling editable mode for $(PACKAGE_REFERENCE) (if present)"
	@if conan editable list | grep -q "$(PACKAGE_REFERENCE)"; then \
		conan editable remove -r "*" || { echo 'Failed to disable editable mode'; exit 1; }; \
		echo "Editable mode DISABLED for $(PACKAGE_REFERENCE)"; \
	else \
		echo "Package $(PACKAGE_REFERENCE) is not in editable mode"; \
	fi

editable_status: ## Show whether the local Matter package is in editable mode
	@echo "Checking editable status for $(PACKAGE_REFERENCE)" 
	@if conan editable list | grep -q "$(PACKAGE_REFERENCE)"; then \
		echo "Status: ENABLED"; \
	else \
		echo "Status: DISABLED"; \
	fi

remove_matter_packages: ## Remove all local matter packages
	@echo "Removing all matter packages"
	conan remove "mat*" --confirm 

remove_all_packages: ## Remove all local conan packages
	@echo "Removing all local packages"
	conan remove "*" --confirm

package_version: ## Display the package version
	@echo "Package version: $(PACKAGE_VERSION)"

create_stack_package: package_version ## Build the stack package
	@echo "Creating matter stack package with version $(PACKAGE_VERSION)"
	conan export-pkg packages/matter/conanfile.py

create_app_package: package_version ## Build the app package
	conan export-pkg packages/matter_app/conanfile.py

install_app_package: package_version ## Install the app package
	@echo "Installing app package from packages/matter_app/pkg.slt..."
	slt install -f packages/matter_app/pkg.slt

install_stack_package: package_version ## Install the stack package
	@echo "Installing stack package from packages/matter/pkg.slt..."
	slt install -f packages/matter/pkg.slt

install_remotes: ## Install the remotes
	@echo "Installing remotes from packages/remotes.json"
	conan config install -t file packages/remotes.json

update_slce_extra: ## Update the SLCE extra
	@echo "Updating SLCE extra"
	python3 slc/script/get_slce_extra_paths.py

generate_pkg_slt: ## Generate the pkg.slt file
	@echo "Generating pkg.slt"
	python3 slc/script/generate_pkg_slt.py --verbose -d slc --matter-version $(PACKAGE_VERSION)

generate_pkg_slt_common: ## Generate the pkg.slt.common file
	@echo "Generating pkg.slt common"
	python3 slc/script/generate_pkg_slt.py --verbose -d slc --common --matter-version $(PACKAGE_VERSION)

upload_app_package: package_version ## Upload the app package
	@echo "Uploading app package (version $(PACKAGE_VERSION))..."
	conan upload matter_app/$(PACKAGE_VERSION)@silabs -r matter-conan-dev

upload_stack_package: package_version ## Upload the stack package
	@echo "Uploading stack package (version $(PACKAGE_VERSION))..."
	conan upload matter/$(PACKAGE_VERSION)@silabs -r matter-conan-dev

comment_revision_mode: ## Comment out the revision_mode = "scm" line in conanfile.py files
	@echo "Commenting out revision_mode = \"scm\" in conanfile.py files"
	@for file in packages/*/conanfile.py; do \
		if [ -f "$$file" ]; then \
			if grep -q "^[[:space:]]*self\.revision_mode = \"scm\"" "$$file"; then \
				sed -i '' 's/^[[:space:]]*self\.revision_mode = "scm"/        # self.revision_mode = "scm"/' "$$file"; \
				echo "Commented revision_mode in $$file"; \
			else \
				echo "No uncommented revision_mode found in $$file"; \
			fi; \
		fi; \
	done

uncomment_revision_mode: ## Uncomment the revision_mode = "scm" line in conanfile.py files
	@echo "Uncommenting revision_mode = \"scm\" in conanfile.py files"
	@for file in packages/*/conanfile.py; do \
		if [ -f "$$file" ]; then \
			if grep -q "^[[:space:]]*# self\.revision_mode = \"scm\"" "$$file"; then \
				sed -i '' 's/^[[:space:]]*# self\.revision_mode = "scm"/        self.revision_mode = "scm"/' "$$file"; \
				echo "Uncommented revision_mode in $$file"; \
			else \
				echo "No commented revision_mode found in $$file"; \
			fi; \
		fi; \
	done
