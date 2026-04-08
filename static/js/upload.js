// AutoCaption AI - Simple JavaScript
// This file handles all the interactive features

document.addEventListener("DOMContentLoaded", function() {
    
    // ============================================
    // PLATFORM SELECTOR - Choose social media platform
    // ============================================
    var platformGrid = document.getElementById("platformGrid");
    var platformInput = document.getElementById("platform-input");

    if (platformGrid) {
        platformGrid.addEventListener("click", function(e) {
            var chip = e.target.closest(".platform-chip");
            if (!chip) return;

            // Remove active class from all chips
            var chips = platformGrid.querySelectorAll(".platform-chip");
            for (var i = 0; i < chips.length; i++) {
                chips[i].classList.remove("active");
            }

            // Add active class to clicked chip
            chip.classList.add("active");

            // Update hidden input value
            if (platformInput) {
                platformInput.value = chip.dataset.platform;
            }
        });
    }

    // ============================================
    // CAPTION TYPE SELECTOR - Choose caption type
    // ============================================
    var captionTypeOptions = document.getElementById("captionTypeOptions");
    var selectedCaptionType = "all";

    if (captionTypeOptions) {
        captionTypeOptions.addEventListener("click", function(e) {
            var btn = e.target.closest(".caption-type-btn");
            if (!btn) return;

            // Remove active from all buttons
            var buttons = captionTypeOptions.querySelectorAll(".caption-type-btn");
            for (var i = 0; i < buttons.length; i++) {
                buttons[i].classList.remove("active");
            }

            // Add active to clicked button
            btn.classList.add("active");
            selectedCaptionType = btn.dataset.type;
        });
    }

    // ============================================
    // FILE UPLOAD - Handle image selection
    // ============================================
    var dropZone = document.getElementById("drop-zone");
    var fileInput = document.getElementById("file-input");
    var generateBtn = document.getElementById("generateBtn");
    var selectedFileDisplay = document.getElementById("selectedFileDisplay");
    var selectedFileName = document.getElementById("selectedFileName");
    var clearFileBtn = document.getElementById("clearFileBtn");
    var resultsArea = document.getElementById("results-area");
    var loadingState = document.getElementById("loading-state");
    var captionsContainer = document.getElementById("captions-container");
    var errorContainer = document.getElementById("error-message");
    var errorText = document.getElementById("error-text");
    var selectedFile = null;

    // Click on drop zone opens file browser
    if (dropZone && fileInput) {
        dropZone.addEventListener("click", function() {
            fileInput.click();
        });

        // Drag and drop functionality
        dropZone.addEventListener("dragover", function(e) {
            e.preventDefault();
            dropZone.classList.add("dragover");
        });

        dropZone.addEventListener("dragleave", function() {
            dropZone.classList.remove("dragover");
        });

        dropZone.addEventListener("drop", function(e) {
            e.preventDefault();
            dropZone.classList.remove("dragover");
            if (e.dataTransfer.files.length) {
                handleFileSelect(e.dataTransfer.files[0]);
            }
        });

        // File selected from browser
        fileInput.addEventListener("change", function(e) {
            if (e.target.files.length) {
                handleFileSelect(e.target.files[0]);
            }
        });
    }

    // Function to handle selected file
    function handleFileSelect(file) {
        // Hide any previous errors
        if (errorContainer) {
            errorContainer.classList.add("hidden");
        }

        // Check file type
        var validTypes = ["image/jpeg", "image/png", "image/gif", "image/webp"];
        if (validTypes.indexOf(file.type) === -1) {
            showError("Please upload a JPEG, PNG, GIF, or WebP image.");
            return;
        }

        // Check file size (max 16MB)
        if (file.size > 16 * 1024 * 1024) {
            showError("File is too large. Maximum size is 16MB.");
            return;
        }

        // Store file and update UI
        selectedFile = file;
        if (selectedFileName) selectedFileName.textContent = file.name;
        if (selectedFileDisplay) selectedFileDisplay.classList.remove("hidden");
        if (generateBtn) generateBtn.disabled = false;
        if (dropZone) dropZone.classList.add("hidden");
        if (resultsArea) resultsArea.classList.add("hidden");
    }

    // Function to show error message
    function showError(message) {
        errorText.textContent = message;
        errorContainer.classList.remove("hidden");
        if (resultsArea) resultsArea.classList.add("hidden");
    }

    // Clear file button
    if (clearFileBtn) {
        clearFileBtn.addEventListener("click", function() {
            selectedFile = null;
            if (fileInput) fileInput.value = "";
            if (selectedFileDisplay) selectedFileDisplay.classList.add("hidden");
            if (generateBtn) {
                generateBtn.disabled = true;
                generateBtn.classList.remove("loading");
            }
            if (dropZone) dropZone.classList.remove("hidden");
            if (resultsArea) resultsArea.classList.add("hidden");
        });
    }

    // ============================================
    // GENERATE BUTTON - Create captions
    // ============================================
    var captionHint = document.getElementById("captionHint");
    var imagePreview = document.getElementById("image-preview");
    var resultPlatformBadge = document.getElementById("resultPlatformBadge");
    var currentCaptions = {};
    var selectedCaptionKey = null;
    var currentFilename = null;

    if (generateBtn) {
        generateBtn.addEventListener("click", function() {
            if (!selectedFile || generateBtn.disabled || generateBtn.classList.contains("loading")) {
                return;
            }

            // Show loading state
            generateBtn.disabled = true;
            generateBtn.classList.add("loading");
            if (resultsArea) resultsArea.classList.remove("hidden");
            if (loadingState) {
                loadingState.classList.remove("hidden");
                loadingState.classList.add("flex");
            }
            if (captionsContainer) {
                captionsContainer.classList.add("hidden");
                captionsContainer.classList.remove("flex");
            }

            // Show image preview
            var reader = new FileReader();
            reader.onload = function(e) {
                if (imagePreview) imagePreview.src = e.target.result;
            };
            reader.readAsDataURL(selectedFile);

            // Upload to server
            uploadImage(selectedFile);
        });
    }

    // Function to upload image and get captions
    function uploadImage(file) {
        var formData = new FormData();
        formData.append("image", file);

        // Get selected platform
        var platform = "general";
        if (platformInput) {
            platform = platformInput.value;
        }
        formData.append("platform", platform);

        // Get caption hint
        var hint = "";
        if (captionHint) {
            hint = captionHint.value.trim();
        }
        if (hint) {
            formData.append("caption_hint", hint);
        }
        formData.append("caption_type", selectedCaptionType);

        // Send to server
        fetch("/upload", {
            method: "POST",
            body: formData
        })
        .then(function(response) {
            if (!response.ok) {
                return response.json().then(function(errData) {
                    throw new Error(errData.error || "An error occurred.");
                });
            }
            return response.json();
        })
        .then(function(data) {

            // Store captions
            currentCaptions = {
                descriptive: data.captions.descriptive || "No description available.",
                social: data.captions.social || "No caption available.",
                accessibility: data.captions.accessibility || "No alt-text available."
            };

            // Store filename for regeneration
            currentFilename = data.filename;

            // Update preview buttons
            var optDescPreview = document.getElementById("optDescPreview");
            var optSocialPreview = document.getElementById("optSocialPreview");
            var optAltPreview = document.getElementById("optAltPreview");

            if (optDescPreview) optDescPreview.textContent = truncateText(currentCaptions.descriptive, 60);
            if (optSocialPreview) optSocialPreview.textContent = truncateText(currentCaptions.social, 60);
            if (optAltPreview) optAltPreview.textContent = truncateText(currentCaptions.accessibility, 60);

            // Show/hide caption buttons based on type
            var descBtn = document.getElementById("captionOptDesc");
            var socialBtn = document.getElementById("captionOptSocial");
            var altBtn = document.getElementById("captionOptAlt");

            if (selectedCaptionType === "all") {
                if (descBtn) descBtn.style.display = "flex";
                if (socialBtn) socialBtn.style.display = "flex";
                if (altBtn) altBtn.style.display = "flex";
            } else if (selectedCaptionType === "descriptive") {
                if (descBtn) descBtn.style.display = "flex";
                if (socialBtn) socialBtn.style.display = "none";
                if (altBtn) altBtn.style.display = "none";
            } else if (selectedCaptionType === "social") {
                if (descBtn) descBtn.style.display = "none";
                if (socialBtn) socialBtn.style.display = "flex";
                if (altBtn) altBtn.style.display = "none";
            } else if (selectedCaptionType === "accessibility") {
                if (descBtn) descBtn.style.display = "none";
                if (socialBtn) socialBtn.style.display = "none";
                if (altBtn) altBtn.style.display = "flex";
            }

            // Update platform badge
            if (resultPlatformBadge) {
                resultPlatformBadge.textContent = data.platform_name || "General";
            }

            // Show results
            if (loadingState) {
                loadingState.classList.add("hidden");
                loadingState.classList.remove("flex");
            }
            if (captionsContainer) {
                captionsContainer.classList.remove("hidden");
                captionsContainer.classList.add("flex");
            }

            // Select social caption by default
            selectCaption("social");

        })
        .catch(function(error) {
            showError("Error: " + error.message);
            if (loadingState) {
                loadingState.classList.add("hidden");
                loadingState.classList.remove("flex");
            }
        });
    }

    // Helper function to truncate text
    function truncateText(text, maxLength) {
        if (!text) return "--";
        if (text.length > maxLength) {
            return text.substring(0, maxLength) + "...";
        }
        return text;
    }

    // ============================================
    // CAPTION SELECTION - Click to select caption
    // ============================================
    var selectedCaptionText = document.getElementById("selectedCaptionText");
    var selectedCaptionArea = document.getElementById("selectedCaptionArea");

    function selectCaption(key) {
        if (!currentCaptions[key]) return;

        selectedCaptionKey = key;

        // Update button states
        var buttons = document.querySelectorAll(".caption-option-btn");
        for (var i = 0; i < buttons.length; i++) {
            buttons[i].classList.remove("active");
            if (buttons[i].dataset.captionKey === key) {
                buttons[i].classList.add("active");
            }
        }

        // Update displayed caption
        if (selectedCaptionText) {
            selectedCaptionText.classList.add("fade-out");
        }
        if (selectedCaptionArea) {
            selectedCaptionArea.classList.add("caption-updating");
        }

        setTimeout(function() {
            if (selectedCaptionText) {
                selectedCaptionText.textContent = currentCaptions[key];
                selectedCaptionText.classList.remove("fade-out");
                selectedCaptionText.classList.add("fade-in");
            }

            setTimeout(function() {
                if (selectedCaptionText) {
                    selectedCaptionText.classList.remove("fade-in");
                }
                if (selectedCaptionArea) {
                    selectedCaptionArea.classList.remove("caption-updating");
                }
            }, 400);
        }, 300);
    }

    // Add click handlers to caption option buttons
    var captionButtons = document.querySelectorAll(".caption-option-btn");
    for (var i = 0; i < captionButtons.length; i++) {
        captionButtons[i].addEventListener("click", function() {
            var key = this.dataset.captionKey;
            selectCaption(key);
        });
    }

    // ============================================
    // COPY BUTTON - Copy caption to clipboard
    // ============================================
    var copySelectedBtn = document.getElementById("copySelectedBtn");

    if (copySelectedBtn) {
        copySelectedBtn.addEventListener("click", function() {
            if (!selectedCaptionKey || !currentCaptions[selectedCaptionKey]) return;

            navigator.clipboard.writeText(currentCaptions[selectedCaptionKey]).then(function() {
                var originalHTML = copySelectedBtn.innerHTML;
                copySelectedBtn.classList.add("copied");
                copySelectedBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg><span>Copied!</span>';
                setTimeout(function() {
                    copySelectedBtn.innerHTML = originalHTML;
                    copySelectedBtn.classList.remove("copied");
                }, 2000);
            });
        });
    }

    // ============================================
    // REGENERATE BUTTON - Create new captions
    // ============================================
    var regenerateBtn = document.getElementById("regenerateBtn");
    var isRegenerating = false;
    var loadingText = document.querySelector(".loading-text");
    var loadingSubtext = document.querySelector(".loading-subtext");

    if (regenerateBtn) {
        regenerateBtn.addEventListener("click", function() {
            if (isRegenerating || !currentFilename) return;

            isRegenerating = true;
            regenerateBtn.disabled = true;
            regenerateBtn.classList.add("regenerating");

            // Show loading
            if (captionsContainer) {
                captionsContainer.classList.add("hidden");
                captionsContainer.classList.remove("flex");
            }
            if (loadingState) {
                loadingState.classList.remove("hidden");
                loadingState.classList.add("flex");
            }
            if (loadingText) loadingText.textContent = "Regenerating captions";
            if (loadingSubtext) loadingSubtext.textContent = "Creating new captions...";

            var platform = "general";
            if (platformInput) platform = platformInput.value;

            var hint = "";
            if (captionHint) hint = captionHint.value.trim();

            fetch("/regenerate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    filename: currentFilename,
                    platform: platform,
                    caption_hint: hint,
                    caption_type: selectedCaptionType
                })
            })
            .then(function(response) {
                if (!response.ok) {
                    return response.json().then(function(errData) {
                        throw new Error(errData.error || "Regeneration failed.");
                    });
                }
                return response.json();
            })
            .then(function(data) {

                // Update captions
                currentCaptions = {
                    descriptive: data.captions.descriptive || "No description available.",
                    social: data.captions.social || "No caption available.",
                    accessibility: data.captions.accessibility || "No alt-text available."
                };

                // Update previews
                var optDescPreview = document.getElementById("optDescPreview");
                var optSocialPreview = document.getElementById("optSocialPreview");
                var optAltPreview = document.getElementById("optAltPreview");

                if (optDescPreview) optDescPreview.textContent = truncateText(currentCaptions.descriptive, 60);
                if (optSocialPreview) optSocialPreview.textContent = truncateText(currentCaptions.social, 60);
                if (optAltPreview) optAltPreview.textContent = truncateText(currentCaptions.accessibility, 60);

                // Update platform badge
                if (resultPlatformBadge) {
                    resultPlatformBadge.textContent = data.platform_name || "General";
                }

                // Show captions
                if (loadingState) {
                    loadingState.classList.add("hidden");
                    loadingState.classList.remove("flex");
                }
                if (captionsContainer) {
                    captionsContainer.classList.remove("hidden");
                    captionsContainer.classList.add("flex");
                }

                // Re-select current caption
                if (selectedCaptionKey) {
                    selectCaption(selectedCaptionKey);
                } else {
                    selectCaption("social");
                }

            })
            .catch(function(error) {
                // Show error but keep results visible
                if (loadingState) {
                    loadingState.classList.add("hidden");
                    loadingState.classList.remove("flex");
                }
                if (captionsContainer) {
                    captionsContainer.classList.remove("hidden");
                    captionsContainer.classList.add("flex");
                }
                errorText.textContent = "Regeneration failed: " + error.message;
                errorContainer.classList.remove("hidden");
                setTimeout(function() {
                    errorContainer.classList.add("hidden");
                }, 5000);
            })
            .finally(function() {
                isRegenerating = false;
                regenerateBtn.disabled = false;
                regenerateBtn.classList.remove("regenerating");
                if (loadingText) loadingText.textContent = "Analyzing image with AI";
                if (loadingSubtext) loadingSubtext.textContent = "Generating platform-optimized captions...";
            });
        });
    }

    // ============================================
    // GALLERY - View saved images and captions
    // ============================================
    var galleryGrid = document.getElementById("galleryGrid");
    var galleryModal = document.getElementById("galleryModal");
    var galleryModalClose = document.getElementById("galleryModalClose");

    if (galleryGrid && galleryModal) {
        galleryGrid.addEventListener("click", function(e) {
            var card = e.target.closest(".gallery-card");
            if (!card) return;

            // Get data from card
            var filename = card.dataset.filename;
            var descriptive = card.dataset.descriptive;
            var social = card.dataset.social;
            var alt = card.dataset.alt;
            var platform = card.dataset.platform;
            var timestamp = card.dataset.timestamp;

            // Fill modal with data
            document.getElementById("modalImage").src = "/static/uploads/" + filename;
            document.getElementById("modalImage").alt = alt || "Uploaded image";
            document.getElementById("modalPlatform").textContent = platform || "general";
            document.getElementById("modalDate").textContent = timestamp || "";
            document.getElementById("modalDescriptive").textContent = descriptive || "No description available.";
            document.getElementById("modalSocial").textContent = social || "No caption available.";
            document.getElementById("modalAlt").textContent = alt || "No alt-text available.";

            // Show modal
            galleryModal.classList.add("visible");
            document.body.style.overflow = "hidden";
        });

        // Close modal functions
        function closeGalleryModal() {
            galleryModal.classList.remove("visible");
            document.body.style.overflow = "";
        }

        if (galleryModalClose) {
            galleryModalClose.addEventListener("click", closeGalleryModal);
        }

        galleryModal.addEventListener("click", function(e) {
            if (e.target === galleryModal) closeGalleryModal();
        });

        document.addEventListener("keydown", function(e) {
            if (e.key === "Escape") {
                closeGalleryModal();
            }
        });
    }

    // ============================================
    // CLEAR HISTORY - Delete all gallery items
    // ============================================
    var clearHistoryBtn = document.getElementById("clearHistoryBtn");
    var clearHistoryModal = document.getElementById("clearHistoryModal");
    var confirmClearHistory = document.getElementById("confirmClearHistory");
    var cancelClearHistory = document.getElementById("cancelClearHistory");

    if (clearHistoryBtn && clearHistoryModal) {
        clearHistoryBtn.addEventListener("click", function() {
            clearHistoryModal.classList.add("visible");
        });
    }

    if (cancelClearHistory && clearHistoryModal) {
        cancelClearHistory.addEventListener("click", function() {
            clearHistoryModal.classList.remove("visible");
        });
    }

    if (confirmClearHistory && clearHistoryModal) {
        confirmClearHistory.addEventListener("click", function() {
            confirmClearHistory.disabled = true;
            confirmClearHistory.textContent = "Clearing...";

            fetch("/reset", { method: "POST" })
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    if (data.success) {
                        localStorage.clear();
                        sessionStorage.clear();
                        window.location.href = "/gallery?t=" + Date.now();
                    }
                })
                .catch(function(err) {
                    console.error("Clear failed:", err);
                    confirmClearHistory.textContent = "Error - Try Again";
                    confirmClearHistory.disabled = false;
                });
        });
    }

    if (clearHistoryModal) {
        clearHistoryModal.addEventListener("click", function(e) {
            if (e.target === clearHistoryModal) {
                clearHistoryModal.classList.remove("visible");
            }
        });
    }

});