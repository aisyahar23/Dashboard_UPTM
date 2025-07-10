// Enhanced GSAP Animations
gsap.registerPlugin();

// Page load animations
gsap.timeline()
    .from("#animationContainer", {
        duration: 1.2,
        x: -200,
        opacity: 0,
        ease: "power3.out"
    })
    .from("#loginContainer", {
        duration: 1.2,
        x: 200,
        opacity: 0,
        ease: "power3.out"
    }, "-=0.8")
    .from("#admin", {
        duration: 1.8,
        y: 0,
        scale: 1,
        opacity: 1,
        ease: "bounce.out"
    }, "-=0.5")
    .from("#dataCard1, #dataCard2, #dataCard3", {
        duration: 1,
        scale: 0,
        opacity: 0,
        ease: "back.out(1.7)",
        stagger: 0.2
    }, "-=0.8")
    .from("#floatingCard1, #floatingCard2, #floatingCard3", {
        duration: 1.2,
        scale: 0,
        opacity: 0,
        rotation: 360,
        ease: "back.out(1.7)",
        stagger: 0.3
    }, "-=0.6")
    .from("#notification1, #notification2", {
        duration: 0.8,
        scale: 0,
        rotation: 360,
        ease: "elastic.out(1, 0.5)",
        stagger: 0.3
    }, "-=0.5");

// Form interactions
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const emailCheck = document.getElementById('emailCheck');
const emailHint = document.getElementById('emailHint');
const strengthBar = document.getElementById('strengthBar');
const strengthText = document.getElementById('strengthText');
const togglePassword = document.getElementById('togglePassword');
const rememberCheckbox = document.getElementById('rememberMe');
const checkboxBg = document.getElementById('checkboxBg');
const checkIcon = document.getElementById('checkIcon');
const loginBtn = document.getElementById('loginBtn');

// Enhanced email validation
emailInput.addEventListener('input', (e) => {
    const email = e.target.value;
    const isValid = email.includes('@') && email.includes('.');
    
    if (isValid) {
        gsap.to(emailCheck, { opacity: 1, scale: 1.1, duration: 0.3 });
        emailHint.style.opacity = '1';
        emailHint.textContent = 'Format e-mel yang sah ✓';
        emailHint.className = 'text-xs text-green-500 mt-2 transition-opacity duration-300';
    } else if (email.length > 0) {
        gsap.to(emailCheck, { opacity: 0, scale: 1, duration: 0.3 });
        emailHint.style.opacity = '1';
        emailHint.textContent = 'Sila masukkan alamat e-mel yang sah';
        emailHint.className = 'text-xs text-red-500 mt-2 transition-opacity duration-300';
    } else {
        gsap.to(emailCheck, { opacity: 0, scale: 1, duration: 0.3 });
        emailHint.style.opacity = '0';
    }
});

// Enhanced password strength
passwordInput.addEventListener('input', (e) => {
    const password = e.target.value;
    let strength = 0;
    let strengthLabel = 'Lemah';
    let color = '#970747';
    
    if (password.length >= 8) strength += 25;
    if (/[A-Z]/.test(password)) strength += 25;
    if (/[0-9]/.test(password)) strength += 25;
    if (/[^A-Za-z0-9]/.test(password)) strength += 25;
    
    if (strength >= 75) {
        strengthLabel = 'Kuat';
        color = '#10B981';
    } else if (strength >= 50) {
        strengthLabel = 'Baik';
        color = '#1989AC';
    } else if (strength >= 25) {
        strengthLabel = 'Sederhana';
        color = '#F59E0B';
    }
    
    gsap.to(strengthBar, {
        width: strength + '%',
        backgroundColor: color,
        duration: 0.5,
        ease: "power2.out"
    });
    
    strengthText.textContent = strengthLabel;
    strengthText.style.color = color;
});

// Enhanced toggle password
togglePassword.addEventListener('click', () => {
    const type = passwordInput.type === 'password' ? 'text' : 'password';
    passwordInput.type = type;
    
    gsap.to(togglePassword, {
        rotation: 180,
        duration: 0.3,
        ease: "power2.out"
    });
    
    const eyeIcon = document.getElementById('eyeIcon');
    if (type === 'text') {
        eyeIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"></path>
        `;
    } else {
        eyeIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
        `;
    }
});

// Enhanced checkbox
rememberCheckbox.addEventListener('change', (e) => {
    if (e.target.checked) {
        gsap.to(checkboxBg, {
            backgroundColor: '#1989AC',
            borderColor: '#1989AC',
            scale: 1.1,
            duration: 0.3
        });
        gsap.to(checkIcon, { opacity: 1, scale: 1.2, duration: 0.3 });
    } else {
        gsap.to(checkboxBg, {
            backgroundColor: '#E5E7EB',
            borderColor: '#D1D5DB',
            scale: 1,
            duration: 0.3
        });
        gsap.to(checkIcon, { opacity: 0, scale: 1, duration: 0.3 });
    }
});

// Enhanced form submission
document.getElementById('loginFormElement').addEventListener('submit', (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const btnText = document.getElementById('btnText');
    const btnIcon = document.getElementById('btnIcon');
    
    // Check credentials
    if (email === 'uptmXaibig@gmail.com' && password === 'dashboard2025@') {
        gsap.to(loginBtn, {
            scale: 0.95,
            duration: 0.1,
            ease: "power2.out",
            onComplete: () => {
                btnText.textContent = 'Mengesahkan...';
                btnIcon.style.display = 'none';
                
                btnText.innerHTML = `
                    <div class="flex items-center space-x-3">
                        <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>Mengesahkan kelayakan...</span>
                    </div>
                `;
                
                gsap.to(loginBtn, {
                    scale: 1,
                    duration: 0.2,
                    ease: "power2.out"
                });
            }
        });

        setTimeout(() => {
            window.location.replace('/dashboard');
        }, 2500);
    } else {
        // Invalid credentials
        gsap.to(loginBtn, {
            scale: 0.95,
            duration: 0.1,
            ease: "power2.out",
            onComplete: () => {
                btnText.innerHTML = `
                    <div class="flex items-center space-x-3">
                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                        <span>Kelayakan tidak sah!</span>
                    </div>
                `;
                
                gsap.to(loginBtn, {
                    scale: 1,
                    backgroundColor: '#DC2626',
                    duration: 0.2,
                    ease: "power2.out"
                });
                
                // Reset after 3 seconds
                setTimeout(() => {
                    btnText.innerHTML = 'Akses Panel';
                    btnIcon.style.display = 'block';
                    gsap.to(loginBtn, {
                        backgroundColor: '',
                        duration: 0.3
                    });
                }, 3000);
            }
        });
    }
});

// Enhanced stats animation
function animateStats() {
    const graduatesCount = document.getElementById('graduatesCount');
    const reportsCount = document.getElementById('reportsCount');
    const employmentRate = document.getElementById('employmentRate');
    
    gsap.to(graduatesCount, {
        duration: 2.5,
        textContent: 49,
        ease: "power2.out",
        snap: { textContent: 1 }
    });
    
    gsap.to(reportsCount, {
        duration: 2.5,
        textContent: 20,
        ease: "power2.out",
        snap: { textContent: 1 },
        delay: 0.5
    });

    gsap.to(employmentRate, {
        duration: 2.5,
        textContent: 75,
        ease: "power2.out",
        snap: { textContent: 1 },
        delay: 1,
        onUpdate: function() {
            employmentRate.textContent = Math.round(this.targets()[0].textContent) + '%';
        }
    });
}

// Enhanced input focus animations
const formInputs = document.querySelectorAll('input');
formInputs.forEach(input => {
    input.addEventListener('focus', (e) => {
        gsap.to(e.target, {
            duration: 0.3,
            scale: 1.02,
            y: -2,
            ease: "power2.out"
        });
    });

    input.addEventListener('blur', (e) => {
        gsap.to(e.target, {
            duration: 0.3,
            scale: 1,
            y: 0,
            ease: "power2.out"
        });
    });
});

// Continuous animations
function startContinuousAnimations() {
    // Admin character stays perfectly still in center - no breathing animation
    // Only the laptop screen charts animate
}

// Enhanced parallax mouse effect
document.addEventListener('mousemove', (e) => {
    const mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
    const mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
    
    // Admin character stays perfectly centered - NO MOUSE MOVEMENT
    // Only background particles follow mouse slightly
    gsap.to('#dataParticles circle, #dataParticles rect, #dataParticles polygon', {
        duration: 4,
        x: mouseX * 8,
        y: mouseY * 6,
        ease: "power2.out",
        stagger: 0.3
    });
});

// Initialize everything
document.addEventListener('DOMContentLoaded', () => {
    animateStats();
    startContinuousAnimations();
});
