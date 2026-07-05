/*
 * admin.js — powers the /admin dashboard only.
 * Every action calls a Flask JSON API endpoint (routes/admin.py), which
 * is protected by the session-based login — this file never talks to
 * Supabase directly, and holds no secrets.
 */

function flashMessage(containerId, message, isError = false) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.textContent = message;
  el.classList.remove('admin-success', 'admin-error-box');
  el.classList.add(isError ? 'admin-error-box' : 'admin-success');
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 3000);
}

async function apiRequest(url, options = {}) {
  const res = await fetch(url, {
    credentials: 'same-origin',
    headers: options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

// ---------------- Profile / Hero / About ----------------
const profileForm = document.getElementById('profileForm');
if (profileForm) {
  profileForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      hero_title: document.getElementById('heroTitle').value,
      hero_role: document.getElementById('heroRole').value,
      hero_tagline: document.getElementById('heroTagline').value,
      about_summary: document.getElementById('aboutSummary').value,
      career_objective: document.getElementById('careerObjective').value,
    };
    try {
      await apiRequest('/admin/api/profile', { method: 'PUT', body: JSON.stringify(payload) });
      flashMessage('profileMsg', 'Profile updated successfully.');
    } catch (err) {
      flashMessage('profileMsg', err.message, true);
    }
  });
}

const photoForm = document.getElementById('photoForm');
if (photoForm) {
  photoForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('photoFile');
    if (!fileInput.files[0]) return;
    const formData = new FormData();
    formData.append('photo', fileInput.files[0]);
    try {
      const data = await apiRequest('/admin/api/profile/photo', { method: 'POST', body: formData });
      document.getElementById('currentPhotoPreview').src = data.photo_url;
      flashMessage('photoMsg', 'Profile photo updated.');
    } catch (err) {
      flashMessage('photoMsg', err.message, true);
    }
  });
}

const resumeForm = document.getElementById('resumeForm');
if (resumeForm) {
  resumeForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('resumeFile');
    if (!fileInput.files[0]) return;
    const formData = new FormData();
    formData.append('resume', fileInput.files[0]);
    try {
      await apiRequest('/admin/api/profile/resume', { method: 'POST', body: formData });
      flashMessage('resumeMsg', 'Resume updated.');
    } catch (err) {
      flashMessage('resumeMsg', err.message, true);
    }
  });
}

// ---------------- Contact info ----------------
const contactInfoForm = document.getElementById('contactInfoForm');
if (contactInfoForm) {
  contactInfoForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      email: document.getElementById('contactEmail').value,
      phone: document.getElementById('contactPhone').value,
      location: document.getElementById('contactLocation').value,
    };
    try {
      await apiRequest('/admin/api/contact', { method: 'PUT', body: JSON.stringify(payload) });
      flashMessage('contactInfoMsg', 'Contact info updated.');
    } catch (err) {
      flashMessage('contactInfoMsg', err.message, true);
    }
  });
}

// ---------------- Social links ----------------
const addSocialForm = document.getElementById('addSocialForm');
if (addSocialForm) {
  addSocialForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      platform: document.getElementById('socialPlatform').value,
      url: document.getElementById('socialUrl').value,
      icon: document.getElementById('socialIcon').value,
    };
    try {
      await apiRequest('/admin/api/social-links', { method: 'POST', body: JSON.stringify(payload) });
      flashMessage('socialMsg', 'Social link added. Reloading list…');
      setTimeout(() => window.location.reload(), 800);
    } catch (err) {
      flashMessage('socialMsg', err.message, true);
    }
  });
}
document.querySelectorAll('.delete-social-btn').forEach(btn => {
  btn.addEventListener('click', async () => {
    if (!confirm('Delete this social link?')) return;
    try {
      await apiRequest(`/admin/api/social-links/${btn.dataset.id}`, { method: 'DELETE' });
      btn.closest('.admin-list-row').remove();
    } catch (err) {
      alert(err.message);
    }
  });
});

// ---------------- Skills ----------------
const skillTypeSelect = document.getElementById('newSkillType');
if (skillTypeSelect) {
  function refreshSkillFields() {
    const isTechnical = skillTypeSelect.value === 'technical';
    document.getElementById('skillCategoryField').style.display = isTechnical ? 'block' : 'none';
    document.getElementById('skillLevelField').style.display = isTechnical ? 'block' : 'none';
    document.getElementById('skillIconField').style.display = isTechnical ? 'none' : 'block';
  }
  skillTypeSelect.addEventListener('change', refreshSkillFields);
  refreshSkillFields();
  const levelSlider = document.getElementById('newSkillLevel');
  if (levelSlider) {
    levelSlider.addEventListener('input', () => {
      document.getElementById('skillLevelValue').textContent = levelSlider.value;
    });
  }
}

const addSkillForm = document.getElementById('addSkillForm');
if (addSkillForm) {
  addSkillForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const type = document.getElementById('newSkillType').value;
    const payload = { type, name: document.getElementById('newSkillName').value };
    if (type === 'technical') {
      payload.category = document.getElementById('newSkillCategory').value;
      payload.level = parseInt(document.getElementById('newSkillLevel').value, 10);
    } else {
      payload.icon = document.getElementById('newSkillIcon').value;
    }
    try {
      await apiRequest('/admin/api/skills', { method: 'POST', body: JSON.stringify(payload) });
      flashMessage('skillMsg', 'Skill added. Reloading list…');
      setTimeout(() => window.location.reload(), 800);
    } catch (err) {
      flashMessage('skillMsg', err.message, true);
    }
  });
}
document.querySelectorAll('.delete-skill-btn').forEach(btn => {
  btn.addEventListener('click', async () => {
    if (!confirm('Delete this skill?')) return;
    try {
      await apiRequest(`/admin/api/skills/${btn.dataset.id}`, { method: 'DELETE' });
      btn.closest('.admin-list-row').remove();
    } catch (err) {
      alert(err.message);
    }
  });
});

// ---------------- Projects ----------------
const addProjectForm = document.getElementById('addProjectForm');
if (addProjectForm) {
  addProjectForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      title: document.getElementById('newProjTitle').value,
      tag: document.getElementById('newProjTag').value,
      description: document.getElementById('newProjDesc').value,
      github_link: document.getElementById('newProjGithub').value,
      demo_link: document.getElementById('newProjDemo').value,
    };
    try {
      await apiRequest('/admin/api/projects', { method: 'POST', body: JSON.stringify(payload) });
      flashMessage('projectMsg', 'Project added. Reloading list…');
      setTimeout(() => window.location.reload(), 800);
    } catch (err) {
      flashMessage('projectMsg', err.message, true);
    }
  });
}
document.querySelectorAll('.delete-project-btn').forEach(btn => {
  btn.addEventListener('click', async () => {
    if (!confirm('Delete this project?')) return;
    try {
      await apiRequest(`/admin/api/projects/${btn.dataset.id}`, { method: 'DELETE' });
      btn.closest('.admin-list-row').remove();
    } catch (err) {
      alert(err.message);
    }
  });
});
document.querySelectorAll('.project-image-form').forEach(form => {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const projectId = form.dataset.id;
    const fileInput = form.querySelector('input[type="file"]');
    if (!fileInput.files[0]) return;
    const formData = new FormData();
    formData.append('image', fileInput.files[0]);
    try {
      await apiRequest(`/admin/api/projects/${projectId}/image`, { method: 'POST', body: formData });
      flashMessage('projectMsg', 'Project image uploaded.');
    } catch (err) {
      flashMessage('projectMsg', err.message, true);
    }
  });
});
document.querySelectorAll('.project-screenshots-form').forEach(form => {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const projectId = form.dataset.id;
    const fileInput = form.querySelector('input[type="file"]');
    if (!fileInput.files.length) return;
    const formData = new FormData();
    Array.from(fileInput.files).forEach(f => formData.append('screenshots', f));
    try {
      await apiRequest(`/admin/api/projects/${projectId}/screenshots`, { method: 'POST', body: formData });
      flashMessage('projectMsg', 'Screenshots uploaded.');
    } catch (err) {
      flashMessage('projectMsg', err.message, true);
    }
  });
});

// ---------------- Certifications ----------------
const addCertForm = document.getElementById('addCertForm');
if (addCertForm) {
  addCertForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      title: document.getElementById('newCertTitle').value,
      description: document.getElementById('newCertDesc').value,
      icon: document.getElementById('newCertIcon').value,
    };
    try {
      await apiRequest('/admin/api/certifications', { method: 'POST', body: JSON.stringify(payload) });
      flashMessage('certMsg', 'Certificate added. Reloading list…');
      setTimeout(() => window.location.reload(), 800);
    } catch (err) {
      flashMessage('certMsg', err.message, true);
    }
  });
}
document.querySelectorAll('.delete-cert-btn').forEach(btn => {
  btn.addEventListener('click', async () => {
    if (!confirm('Delete this certificate?')) return;
    try {
      await apiRequest(`/admin/api/certifications/${btn.dataset.id}`, { method: 'DELETE' });
      btn.closest('.admin-list-row').remove();
    } catch (err) {
      alert(err.message);
    }
  });
});
document.querySelectorAll('.cert-image-form').forEach(form => {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const certId = form.dataset.id;
    const fileInput = form.querySelector('input[type="file"]');
    if (!fileInput.files[0]) return;
    const formData = new FormData();
    formData.append('image', fileInput.files[0]);
    try {
      await apiRequest(`/admin/api/certifications/${certId}/image`, { method: 'POST', body: formData });
      flashMessage('certMsg', 'Certificate image uploaded.');
    } catch (err) {
      flashMessage('certMsg', err.message, true);
    }
  });
});

// ---------------- Tab navigation within the dashboard ----------------
document.querySelectorAll('.admin-tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.admin-tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.admin-tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.tab).classList.add('active');
  });
});
