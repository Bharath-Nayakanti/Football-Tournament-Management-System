// league_details.js - Complete Updated Version

/**
 * Initialize when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get league ID from data attribute
    const leagueData = document.getElementById('league-data');
    const leagueId = leagueData ? leagueData.dataset.leagueId : null;
    
    if (!leagueId) {
        console.error("League ID not found in #league-data element");
        return;
    }

    // Initialize all components
    initTabs();
    setupFixturesTab(leagueId);
    setupGenerateButton(leagueId);
    createParticles();
});

/**
 * Set up fixtures tab functionality
 */
function setupFixturesTab(leagueId) {
    const fixturesTab = document.querySelector('[data-tab="fixtures"]');
    if (fixturesTab) {
        // Load fixtures when tab is clicked
        fixturesTab.addEventListener('click', () => loadFixtures(leagueId));
        
        // Pre-load if already on fixtures tab
        if (fixturesTab.classList.contains('active')) {
            loadFixtures(leagueId);
        }
    }
}

/**
 * Set up generate fixtures button
 */
function setupGenerateButton(leagueId) {
    const generateBtn = document.getElementById('generate-fixtures-btn');
    if (generateBtn) {
        generateBtn.addEventListener('click', async () => {
            const matchesPerDay = prompt('How many matches should be played each day?', '2');
            
            // Validate input
            if (matchesPerDay === null) return; // User cancelled
            if (!matchesPerDay || isNaN(matchesPerDay) || parseInt(matchesPerDay) < 1) {
                showFlashMessage('Please enter a valid number greater than 0', 'error');
                return;
            }

            await generateFixtures(leagueId, parseInt(matchesPerDay));
        });
    }
}

/**
 * Generate fixtures for league
 */
async function generateFixtures(leagueId, matchesPerDay = 2) {
    const btn = document.getElementById('generate-fixtures-btn');
    if (!btn) return;
    
    try {
        // Show loading state
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        
        // Make API request
        const response = await fetch(`/leagues/${leagueId}/generate-fixtures`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ matches_per_day: matchesPerDay })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Success handling
            btn.classList.add('animate__heartBeat');
            setTimeout(() => btn.classList.remove('animate__heartBeat'), 1000);
            
            showFlashMessage(result.message || 'Fixtures generated successfully!', 'success');
            await loadFixtures(leagueId); // Refresh fixtures display
        } else {
            throw new Error(result.error || 'Failed to generate fixtures');
        }
    } catch (error) {
        console.error('Fixture generation error:', error);
        showFlashMessage(error.message, 'error');
    } finally {
        // Reset button state
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-magic"></i> Generate Fixtures';
    }
}

/**
 * Load and display fixtures from API
 */
async function loadFixtures(leagueId) {
    const tableBody = document.getElementById('fixtures-table-body');
    if (!tableBody) return;
    
    try {
        // Show loading state
        tableBody.innerHTML = `
            <tr class="loading-state">
                <td colspan="4">
                    <i class="fas fa-spinner fa-spin"></i> Loading fixtures...
                </td>
            </tr>
        `;
        
        // Fetch fixtures
        const response = await fetch(`/leagues/${leagueId}/fixtures`);
        const fixtures = await response.json();
        
        // Handle empty state
        if (!fixtures || fixtures.length === 0) {
            tableBody.innerHTML = `
                <tr class="empty-state animate__animated animate__fadeIn">
                    <td colspan="4">
                        <i class="fas fa-calendar-plus"></i>
                        <p>No fixtures generated yet</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        // Render fixtures
        tableBody.innerHTML = fixtures.map(fixture => `
            <tr class="animate__animated animate__fadeIn">
                <td>${formatFixtureDate(fixture.date)}</td>
                <td>
                    <div class="match-cell">
                        ${createTeamBadge(fixture.home_team)}
                        <span class="vs-separator">vs</span>
                        ${createTeamBadge(fixture.away_team)}
                    </div>
                </td>
                <td>
                    <span class="status-badge ${fixture.status.toLowerCase()}">
                        ${fixture.status}
                    </span>
                </td>
                <td>
                    ${fixture.status === 'Pending' ? 
                        createEditButton(fixture.id) : 
                        createScoreDisplay(fixture.home_score, fixture.away_score)
                    }
                </td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error("Failed to load fixtures:", error);
        tableBody.innerHTML = `
            <tr class="error-state">
                <td colspan="4">
                    <i class="fas fa-exclamation-triangle"></i>
                    Failed to load fixtures
                </td>
            </tr>
        `;
    }
}

/**
 * Helper: Format fixture date
 */
function formatFixtureDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
    });
}

/**
 * Helper: Create team badge element
 */
function createTeamBadge(teamName) {
    return `
        <div class="team-badge">
            <div class="logo"><i class="fas fa-shield-alt"></i></div>
            <span>${teamName}</span>
        </div>
    `;
}

/**
 * Helper: Create edit score button
 */
function createEditButton(fixtureId) {
    return `
        <button class="btn-icon update-score" data-id="${fixtureId}">
            <i class="fas fa-edit"></i>
        </button>
    `;
}

/**
 * Helper: Create score display
 */
function createScoreDisplay(homeScore, awayScore) {
    return `
        <span class="score-display">
            ${homeScore || '0'} - ${awayScore || '0'}
        </span>
    `;
}

/**
 * Show flash messages
 */
function showFlashMessage(message, type) {
    const flashContainer = document.querySelector('.flash-container');
    if (!flashContainer) return;
    
    // Create message element
    const flashMessage = document.createElement('div');
    flashMessage.className = `flash-message flash-${type} animate__animated animate__slideInDown`;
    flashMessage.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        ${message}
    `;
    
    // Add to container
    flashContainer.appendChild(flashMessage);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        flashMessage.classList.add('animate__fadeOut');
        setTimeout(() => flashMessage.remove(), 500);
    }, 5000);
}

/**
 * Initialize tab functionality
 */
function initTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            // Update active tab button
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Update active tab content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(this.getAttribute('data-tab')).classList.add('active');
        });
    });
}

/**
 * Create animated background particles
 */
function createParticles() {
    const container = document.querySelector('.particles');
    if (!container) return;
    
    // Clear existing particles
    container.innerHTML = '';
    
    // Create new particles
    const particleCount = 30;
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Random properties
        particle.style.width = `${Math.random() * 5 + 2}px`;
        particle.style.height = particle.style.width;
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        particle.style.animationDelay = `${Math.random() * 5}s`;
        particle.style.animationDuration = `${Math.random() * 10 + 10}s`;
        
        container.appendChild(particle);
    }
}