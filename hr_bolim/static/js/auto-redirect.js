// Auto-redirect to login page if no jobs available
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is on jobs page and there are no jobs
    const jobsGrid = document.querySelector('.grid.grid-cols-1');
    const emptyState = document.querySelector('.empty-state');
    const loginModal = document.getElementById('autoLoginModal');
    
    if (jobsGrid && emptyState && !loginModal) {
        // Create auto-login modal
        const modal = document.createElement('div');
        modal.id = 'autoLoginModal';
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-8 max-w-md mx-4">
                <div class="text-center">
                    <i class="fas fa-briefcase text-gray-400 text-5xl mb-4"></i>
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">Hech qanday vakansiya yo'q</h3>
                    <p class="text-gray-600 mb-6">Siz 1 soatdan keyin login qilishingiz mumkin. Avtomatik login oynasi ochiladi...</p>
                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <div class="flex items-center">
                            <i class="fas fa-clock text-blue-600 mr-3"></i>
                            <span id="countdown">60</span>
                        </div>
                    </div>
                    <div class="text-sm text-gray-500 mt-4">
                        <p>Login qilish uchun: <strong>1 soatdan keyin</strong></p>
                        <p>Yoki: <a href="{% url 'login' %}" class="text-blue-600 hover:underline">darhol login qiling</a></p>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Start countdown
        let seconds = 60;
        const countdownEl = document.getElementById('countdown');
        
        const timer = setInterval(() => {
            seconds--;
            if (seconds > 0) {
                const minutes = Math.floor(seconds / 60);
                const remainingSeconds = seconds % 60;
                countdownEl.textContent = `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
            } else {
                countdownEl.textContent = '0:00';
                clearInterval(timer);
                // Redirect to login after countdown
                setTimeout(() => {
                    window.location.href = '{% url "login" %}';
                }, 1000);
            }
        }, 1000);
        
        // Auto redirect after 60 seconds
        setTimeout(() => {
            window.location.href = '{% url "login" %}';
        }, 61000);
    }
});
