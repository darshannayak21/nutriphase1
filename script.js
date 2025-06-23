document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('profileForm');
    const steps = document.querySelectorAll('.form-step');
    const progressSteps = document.querySelectorAll('.progress-step');
    const nextBtns = document.querySelectorAll('.next-btn');
    const prevBtns = document.querySelectorAll('.prev-btn');
    const resultsContainer = document.getElementById('results');
    const resultsDisplay = document.getElementById('profileResults');
    let currentStep = 0;
    
    // Initialize form steps
    showStep(currentStep);
    
    // Next button functionality
    nextBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            if (validateStep(currentStep)) {
                currentStep++;
                showStep(currentStep);
                updateProgressBar();
            }
        });
    });
    
    // Previous button functionality
    prevBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            currentStep--;
            showStep(currentStep);
            updateProgressBar();
        });
    });
    
    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Gather form data
        const formData = {
            height: form.elements.height.value,
            weight: form.elements.weight.value,
            age: parseInt(form.elements.age.value),
            gender: form.elements.gender.value,
            activity_level: form.elements.activity_level.value,
            medical_conditions: Array.from(form.elements['medical_conditions'])
                .filter(cb => cb.checked && cb.value !== 'none')
                .map(cb => cb.value),
            allergies: Array.from(form.elements.allergies)
                .filter(cb => cb.checked && cb.value !== 'none')
                .map(cb => cb.value),
            diet_type: form.elements.diet_type.value,
            preferences: Array.from(form.elements.preferences)
                .filter(cb => cb.checked)
                .map(cb => cb.value),
            disliked_foods: form.elements.disliked_foods.value,
            main_health_goal: form.elements.main_health_goal.value,
            goal_weight: form.elements.goal_weight.value,
            goal_timeline_weeks: parseInt(form.elements.goal_timeline_weeks.value),
            notes: form.elements.notes.value
        };

        // Send to backend
        try {
            const response = await fetch('http://localhost:5000/calculate_profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                throw new Error('Server responded with an error');
            }
            
            const profile = await response.json();
            displayResults(profile);
        } catch (error) {
            console.error('Error:', error);
            resultsDisplay.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Error creating profile. Please try again.</p>
                    <p>${error.message}</p>
                </div>
            `;
            resultsContainer.classList.remove('hidden');
        }
    });
    
    // Allergy "None" exclusivity
    document.getElementById('allergy_none').addEventListener('change', function() {
        if (this.checked) {
            document.querySelectorAll('.allergy_option').forEach(cb => cb.checked = false);
        }
    });
    
    document.querySelectorAll('.allergy_option').forEach(cb => {
        cb.addEventListener('change', function() {
            if (this.checked) {
                document.getElementById('allergy_none').checked = false;
            }
        });
    });
    
    // Medical Conditions "None" exclusivity
    document.getElementById('medical_none').addEventListener('change', function() {
        if (this.checked) {
            document.querySelectorAll('.medical_option').forEach(cb => cb.checked = false);
        }
    });
    
    document.querySelectorAll('.medical_option').forEach(cb => {
        cb.addEventListener('change', function() {
            if (this.checked) {
                document.getElementById('medical_none').checked = false;
            }
        });
    });
    
    // Helper functions
    function showStep(stepIndex) {
        steps.forEach((step, index) => {
            step.classList.toggle('active', index === stepIndex);
        });
    }
    
    function updateProgressBar() {
        progressSteps.forEach((step, index) => {
            step.classList.toggle('active', index <= currentStep);
        });
    }
    
    function validateStep(stepIndex) {
        const currentStep = steps[stepIndex];
        const requiredFields = currentStep.querySelectorAll('[required]');
        let valid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                valid = false;
                field.style.borderColor = '#F44336';
                field.addEventListener('input', () => {
                    field.style.borderColor = '';
                });
            }
        });
        
        return valid;
    }
    
    function displayResults(profile) {
        let html = `
            <div class="result-section">
                <h3><i class="fas fa-bolt"></i> Energy Profile</h3>
                <div class="result-grid">
                    <div class="result-card">
                        <h4>BMR</h4>
                        <div class="result-value">${profile.bmr}</div>
                        <div class="result-unit">kcal/day</div>
                    </div>
                    <div class="result-card">
                        <h4>TDEE</h4>
                        <div class="result-value">${profile.tdee}</div>
                        <div class="result-unit">kcal/day</div>
                    </div>
                </div>
            </div>
            
            <div class="result-section">
                <h3><i class="fas fa-apple-alt"></i> Nutrition Targets</h3>
                <div class="result-grid">
                    <div class="result-card">
                        <h4>Calories</h4>
                        <div class="result-value">${profile.daily_nutrition_targets.calories.toFixed(0)}</div>
                        <div class="result-unit">kcal/day</div>
                    </div>
                    <div class="result-card">
                        <h4>Protein</h4>
                        <div class="result-value">${profile.daily_nutrition_targets.protein_g.toFixed(1)}</div>
                        <div class="result-unit">g/day</div>
                    </div>
                    <div class="result-card">
                        <h4>Carbs</h4>
                        <div class="result-value">${profile.daily_nutrition_targets.carbs_g.toFixed(1)}</div>
                        <div class="result-unit">g/day</div>
                    </div>
                    <div class="result-card">
                        <h4>Fat</h4>
                        <div class="result-value">${profile.daily_nutrition_targets.fat_g.toFixed(1)}</div>
                        <div class="result-unit">g/day</div>
                    </div>
                    <div class="result-card">
                        <h4>Fiber</h4>
                        <div class="result-value">${profile.daily_nutrition_targets.fiber_g}</div>
                        <div class="result-unit">g/day</div>
                    </div>
                    <div class="result-card">
                        <h4>Water</h4>
                        <div class="result-value">${profile.daily_nutrition_targets.water_ml.toFixed(0)}</div>
                        <div class="result-unit">ml/day</div>
                    </div>
                </div>
            </div>
        `;
        
        // Dietary Recommendations
        const restrictions = profile.restriction_profile;
        if (Object.keys(restrictions).length > 0) {
            html += `
                <div class="result-section">
                    <h3><i class="fas fa-heart"></i> Dietary Recommendations</h3>
                    
                    <div class="food-list">
            `;
            
            if (restrictions.what_to_eat && restrictions.what_to_eat.length > 0) {
                restrictions.what_to_eat.forEach(food => {
                    html += `
                        <div class="food-card good">
                            <i class="fas fa-check-circle"></i> ${food}
                        </div>
                    `;
                });
            }
            
            if (restrictions.what_to_avoid && restrictions.what_to_avoid.length > 0) {
                restrictions.what_to_avoid.forEach(food => {
                    html += `
                        <div class="food-card bad">
                            <i class="fas fa-times-circle"></i> ${food}
                        </div>
                    `;
                });
            }
            
            html += `</div></div>`;
        }
        
        // Compatible Ingredients
        if (profile.ingredient_compatibility_list.length > 0) {
            html += `
                <div class="result-section">
                    <h3><i class="fas fa-check-double"></i> Recommended Ingredients</h3>
                    <div class="food-list">
            `;
            
            profile.ingredient_compatibility_list.forEach(ingredient => {
                html += `
                    <div class="food-card good">
                        <i class="fas fa-leaf"></i> ${ingredient}
                    </div>
                `;
            });
            
            html += `</div></div>`;
        }
        
        resultsDisplay.innerHTML = html;
        resultsContainer.classList.remove('hidden');
        
        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }
});
