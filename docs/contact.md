---
title: Contact Us
hide:
  - navigation
  - toc
---

# Contact Us

Please fill out the form below to get in touch with us. We'll respond as soon as possible.

<form id="contact-form" class="contact-form" onsubmit="handleSubmit(event)">
  
  <!-- Personal Information Section -->
  <div class="form-section">
    <h2>Personal Information</h2>
    
    <div class="form-row">
      <div class="form-group">
        <label for="firstName">First Name <span class="required">*</span></label>
        <input type="text" id="firstName" name="firstName" required>
      </div>
      
      <div class="form-group">
        <label for="lastName">Last Name <span class="required">*</span></label>
        <input type="text" id="lastName" name="lastName" required>
      </div>
    </div>
    
    <div class="form-row">
      <div class="form-group">
        <label for="email">Email Address <span class="required">*</span></label>
        <input type="email" id="email" name="email" required>
      </div>
      
      <div class="form-group">
        <label for="phone">Phone Number <span class="required">*</span></label>
        <input type="tel" id="phone" name="phone" required>
      </div>
    </div>
  </div>
  
  <!-- Vehicle Information Section -->
  <div class="form-section">
    <h2>Vehicle Information</h2>
    
    <div class="form-row">
      <div class="form-group">
        <label for="vehicleYear">Year <span class="required">*</span></label>
        <input type="number" id="vehicleYear" name="vehicleYear" min="1900" max="2030" required>
      </div>
      
      <div class="form-group">
        <label for="vehicleMake">Make <span class="required">*</span></label>
        <input type="text" id="vehicleMake" name="vehicleMake" required>
      </div>
      
      <div class="form-group">
        <label for="vehicleModel">Model <span class="required">*</span></label>
        <input type="text" id="vehicleModel" name="vehicleModel" required>
      </div>
    </div>
  </div>
  
  <!-- Vehicle Condition Section -->
  <div class="form-section">
    <h2>Vehicle Condition <span class="required">*</span></h2>
    
    <div class="condition-options">
      <label class="condition-option">
        <input type="radio" name="condition" value="good" required>
        <span class="condition-option-box">
          <span class="condition-title">Good Condition</span>
          <span class="condition-desc">Well-maintained, vacuumed regularly, and free of stains, pet hair, excessive dirt, or dust.</span>
        </span>
      </label>
      
      <label class="condition-option">
        <input type="radio" name="condition" value="moderate">
        <span class="condition-option-box">
          <span class="condition-title">Moderate Condition</span>
          <span class="condition-desc">Noticeable dirt, some food crumbs, light pet hair, and minor staining.</span>
        </span>
      </label>
      
      <label class="condition-option">
        <input type="radio" name="condition" value="bad">
        <span class="condition-option-box">
          <span class="condition-title">Bad Condition</span>
          <span class="condition-desc">Heavily soiled with significant dirt, food crumbs, excessive pet hair, and large or deep stains.</span>
        </span>
      </label>
    </div>
  </div>
  
  <!-- Services Interested In Section -->
  <div class="form-section">
    <h2>Services Interested In</h2>
    
    <div class="form-group">
      <label>What services are you interested in? <span class="required">*</span></label>
      <div class="checkbox-group">
        <label class="checkbox-label">
          <input type="checkbox" name="services" value="repair" required>
          <span>Vehicle Repair</span>
        </label>
        <label class="checkbox-label">
          <input type="checkbox" name="services" value="maintenance">
          <span>Maintenance Service</span>
        </label>
        <label class="checkbox-label">
          <input type="checkbox" name="services" value="inspection">
          <span>Vehicle Inspection</span>
        </label>
        <label class="checkbox-label">
          <input type="checkbox" name="services" value="parts">
          <span>Parts Replacement</span>
        </label>
        <label class="checkbox-label">
          <input type="checkbox" name="services" value="bodywork">
          <span>Bodywork/Paint</span>
        </label>
        <label class="checkbox-label">
          <input type="checkbox" name="services" value="towing">
          <span>Towing Service</span>
        </label>
        <label class="checkbox-label">
          <input type="checkbox" name="services" value="other">
          <span>Other</span>
        </label>
      </div>
    </div>
    
    <div class="form-group">
      <label for="preferredDate">Preferred Service Date</label>
      <input type="date" id="preferredDate" name="preferredDate">
    </div>
  </div>
  
  <!-- Additional Information Section -->
  <div class="form-section">
    <h2>Additional Information</h2>
    
    <div class="form-group">
      <label for="additionalInfo">Additional Comments or Questions</label>
      <textarea id="additionalInfo" name="additionalInfo" rows="5" 
                placeholder="Please provide any additional information, questions, or special requests..."></textarea>
    </div>
    
    <div class="form-group">
      <label for="howDidYouHear">How did you hear about us?</label>
      <select id="howDidYouHear" name="howDidYouHear">
        <option value="">Please select...</option>
        <option value="search-engine">Search Engine (Google, Bing, etc.)</option>
        <option value="social-media">Social Media</option>
        <option value="referral">Referral from Friend/Family</option>
        <option value="advertisement">Advertisement</option>
        <option value="walk-in">Walk-in</option>
        <option value="other">Other</option>
      </select>
    </div>
  </div>
  
  <!-- Submit Button -->
  <div class="form-section">
    <div class="button-group">
      <button type="button" class="preview-button" onclick="previewJSON()">Preview JSON</button>
      <button type="submit" class="submit-button">Submit Form</button>
    </div>
    <p class="form-note"><span class="required">*</span> indicates required fields</p>
  </div>
  
  <!-- JSON Preview Modal -->
  <div id="jsonModal" class="modal">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Form Data JSON Preview</h3>
        <span class="close-modal" onclick="closeJSONModal()">&times;</span>
      </div>
      <div class="modal-body">
        <pre id="jsonPreview"></pre>
        <div class="modal-actions">
          <button type="button" class="copy-button" onclick="copyJSON()">Copy JSON</button>
          <button type="button" class="close-button" onclick="closeJSONModal()">Close</button>
        </div>
      </div>
    </div>
  </div>
  
</form>

<style>
.contact-form {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
}

.form-section {
  background: var(--md-default-bg-color, #fff);
  border: 1px solid var(--md-default-fg-color--lighter, #e0e0e0);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.form-section h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: var(--md-primary-fg-color, #4051b5);
  font-size: 1.5rem;
  border-bottom: 2px solid var(--md-primary-fg-color, #4051b5);
  padding-bottom: 0.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--md-default-fg-color, #333);
}

.required {
  color: #d32f2f;
  font-weight: bold;
}

.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="tel"],
.form-group input[type="number"],
.form-group input[type="date"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--md-default-fg-color--lighter, #ccc);
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.3s, box-shadow 0.3s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--md-primary-fg-color, #4051b5);
  box-shadow: 0 0 0 3px rgba(64, 81, 181, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.checkbox-label:hover {
  background-color: var(--md-default-bg-color--lightest, #f5f5f5);
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin-right: 0.5rem;
  cursor: pointer;
}

.help-text {
  font-size: 0.875rem;
  color: var(--md-default-fg-color--light, #666);
  margin: 0.25rem 0 0.5rem 0;
}

.submit-button {
  background: var(--md-primary-fg-color, #4051b5);
  color: white;
  border: none;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.1s;
  width: 100%;
  max-width: 300px;
}

.submit-button:hover {
  background: var(--md-primary-fg-color--dark, #303f9f);
  transform: translateY(-1px);
}

.submit-button:active {
  transform: translateY(0);
}

.form-note {
  margin-top: 1rem;
  font-size: 0.875rem;
  color: var(--md-default-fg-color--light, #666);
  text-align: center;
}

/* Vehicle Condition radio options - card style */
.condition-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.condition-option {
  display: flex;
  align-items: flex-start;
  cursor: pointer;
  margin: 0;
}

.condition-option input[type="radio"] {
  margin: 1.25rem 1rem 0 0;
  flex-shrink: 0;
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
}

.condition-option-box {
  flex: 1;
  display: block;
  padding: 1.25rem 1.5rem;
  background: var(--md-default-bg-color--lightest, #f5f5f5);
  border: 1px solid var(--md-default-fg-color--lighter, #e0e0e0);
  border-radius: 8px;
  transition: border-color 0.2s, box-shadow 0.2s, background-color 0.2s;
}

.condition-option:hover .condition-option-box {
  border-color: var(--md-primary-fg-color, #4051b5);
  background: var(--md-default-bg-color--light, #eee);
}

.condition-option input[type="radio"]:checked + .condition-option-box {
  border-color: var(--md-primary-fg-color, #4051b5);
  box-shadow: 0 0 0 2px rgba(64, 81, 181, 0.2);
  background: var(--md-default-bg-color--light, #eee);
}

.condition-title {
  display: block;
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--md-default-fg-color, #333);
  margin-bottom: 0.5rem;
}

.condition-desc {
  display: block;
  font-size: 0.9rem;
  color: var(--md-default-fg-color--light, #666);
  line-height: 1.5;
}

/* Dark mode support */
[data-md-color-scheme="slate"] .form-section {
  background: var(--md-default-bg-color, #1e1e1e);
  border-color: var(--md-default-fg-color--lighter, #404040);
}

[data-md-color-scheme="slate"] .checkbox-label:hover {
  background-color: var(--md-default-bg-color--lightest, #2a2a2a);
}

[data-md-color-scheme="slate"] .condition-option-box {
  background: var(--md-default-bg-color--lightest, #2a2a2a);
  border-color: var(--md-default-fg-color--lighter, #404040);
}

[data-md-color-scheme="slate"] .condition-option:hover .condition-option-box,
[data-md-color-scheme="slate"] .condition-option input[type="radio"]:checked + .condition-option-box {
  background: var(--md-default-bg-color--light, #333);
  border-color: var(--md-primary-fg-color, #4051b5);
}

.button-group {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.preview-button {
  background: var(--md-default-fg-color--light, #666);
  color: white;
  border: none;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.preview-button:hover {
  background: var(--md-default-fg-color, #333);
}

/* Modal Styles */
.modal {
  display: none;
  position: fixed;
  z-index: 1000;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
  background-color: var(--md-default-bg-color, #fff);
  margin: 5% auto;
  padding: 0;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--md-default-fg-color--lighter, #e0e0e0);
}

.modal-header h3 {
  margin: 0;
  color: var(--md-primary-fg-color, #4051b5);
}

.close-modal {
  color: var(--md-default-fg-color--light, #aaa);
  font-size: 28px;
  font-weight: bold;
  cursor: pointer;
  line-height: 1;
}

.close-modal:hover,
.close-modal:focus {
  color: var(--md-default-fg-color, #000);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.modal-body pre {
  background: var(--md-code-bg-color, #f5f5f5);
  border: 1px solid var(--md-default-fg-color--lighter, #e0e0e0);
  border-radius: 4px;
  padding: 1rem;
  overflow-x: auto;
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: 1rem;
  max-height: 50vh;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.copy-button,
.close-button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.copy-button {
  background: var(--md-primary-fg-color, #4051b5);
  color: white;
}

.copy-button:hover {
  background: var(--md-primary-fg-color--dark, #303f9f);
}

.close-button {
  background: var(--md-default-fg-color--light, #666);
  color: white;
}

.close-button:hover {
  background: var(--md-default-fg-color, #333);
}

/* Responsive design */
@media (max-width: 768px) {
  .contact-form {
    padding: 1rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .checkbox-group {
    grid-template-columns: 1fr;
  }
  
  .button-group {
    flex-direction: column;
  }
  
  .submit-button,
  .preview-button {
    width: 100%;
  }
  
  .modal-content {
    width: 95%;
    margin: 10% auto;
  }
}
</style>

<script>
function previewJSON() {
  // Collect form data
  const formData = new FormData(document.getElementById('contact-form'));
  
  // Collect checkbox values as arrays
  const services = Array.from(document.querySelectorAll('input[name="services"]:checked')).map(cb => cb.value);
  
  // Build the data object (same as in handleSubmit)
  const formDataObj = {
    // Personal Information
    firstName: formData.get('firstName'),
    lastName: formData.get('lastName'),
    email: formData.get('email'),
    phone: formData.get('phone'),
    
    // Vehicle Information
    vehicleYear: formData.get('vehicleYear'),
    vehicleMake: formData.get('vehicleMake'),
    vehicleModel: formData.get('vehicleModel'),
    
    // Vehicle Condition (good, moderate, bad)
    condition: formData.get('condition'),
    
    // Services
    services: services,
    preferredDate: formData.get('preferredDate'),
    
    // Additional Information
    additionalInfo: formData.get('additionalInfo'),
    howDidYouHear: formData.get('howDidYouHear')
  };
  
  // Display in modal
  const jsonPreview = document.getElementById('jsonPreview');
  jsonPreview.textContent = JSON.stringify(formDataObj, null, 2);
  
  const modal = document.getElementById('jsonModal');
  modal.style.display = 'block';
  
  // Store for copy function
  window.currentJSON = JSON.stringify(formDataObj, null, 2);
}

function closeJSONModal() {
  const modal = document.getElementById('jsonModal');
  modal.style.display = 'none';
}

function copyJSON() {
  if (window.currentJSON) {
    navigator.clipboard.writeText(window.currentJSON).then(() => {
      const copyBtn = document.querySelector('.copy-button');
      const originalText = copyBtn.textContent;
      copyBtn.textContent = 'Copied!';
      setTimeout(() => {
        copyBtn.textContent = originalText;
      }, 2000);
    }).catch(err => {
      console.error('Failed to copy:', err);
      alert('Failed to copy JSON. Please select and copy manually.');
    });
  }
}

// Close modal when clicking outside of it
window.onclick = function(event) {
  const modal = document.getElementById('jsonModal');
  if (event.target === modal) {
    closeJSONModal();
  }
}

let formSubmitting = false;

async function handleSubmit(event) {
  event.preventDefault();
  
  if (formSubmitting) {
    return;
  }
  
  // Validate required checkboxes for services
  const serviceCheckboxes = document.querySelectorAll('input[name="services"]:checked');
  if (serviceCheckboxes.length === 0) {
    alert('Please select at least one service you are interested in.');
    return;
  }
  
  formSubmitting = true;
  const submitButton = event.target.querySelector('.submit-button');
  const originalButtonText = submitButton.textContent;
  submitButton.disabled = true;
  submitButton.textContent = 'Submitting...';
  
  try {
    // Collect form data
    const formData = new FormData(event.target);
    
    // Collect checkbox values as arrays
    const services = Array.from(document.querySelectorAll('input[name="services"]:checked')).map(cb => cb.value);
    
    // Build the data object
    const formDataObj = {
      // Personal Information
      firstName: formData.get('firstName'),
      lastName: formData.get('lastName'),
      email: formData.get('email'),
      phone: formData.get('phone'),
      
      // Vehicle Information
      vehicleYear: formData.get('vehicleYear'),
      vehicleMake: formData.get('vehicleMake'),
      vehicleModel: formData.get('vehicleModel'),
      
      // Vehicle Condition (good, moderate, bad)
      condition: formData.get('condition'),
      
      // Services
      services: services,
      preferredDate: formData.get('preferredDate'),
      
      // Additional Information
      additionalInfo: formData.get('additionalInfo'),
      howDidYouHear: formData.get('howDidYouHear')
    };
    
    // Log the JSON data to console for debugging
    console.log('=== Form Data JSON ===');
    console.log(JSON.stringify(formDataObj, null, 2));
    console.log('=====================');
    
    // Wrap in formData so n8n workflow can reliably extract it
    const payload = { formData: formDataObj };
    const jsonString = JSON.stringify(payload);
    
    // Log what's being sent
    console.log('=== Sending to Webhook ===');
    console.log('JSON String:', jsonString);
    console.log('========================');
    
    // Send to webhook
    console.log('Sending request to: https://n8n.chefbc.com/webhook/webhook-form');
    const response = await fetch('https://n8n.chefbc.com/webhook/webhook-form', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonString
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json().catch(() => ({ success: true }));
    
    // Log the response
    console.log('=== Webhook Response ===');
    console.log('Status:', response.status);
    console.log('Response:', result);
    console.log('=======================');
    
    // Show success message
    alert('Thank you for your submission! We will contact you soon.');
    
    // Reset the form
    event.target.reset();
    
  } catch (error) {
    console.error('Error submitting form:', error);
    alert('Sorry, there was an error submitting your form. Please try again or contact us directly.');
  } finally {
    formSubmitting = false;
    submitButton.disabled = false;
    submitButton.textContent = originalButtonText;
  }
}
</script>
