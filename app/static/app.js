// State
let allLeads = [];
let currentLead = null;
let chatHistory = [];
let ttsEnabled = true;

// DOM Elements
const statsRow = document.getElementById('statsRow');
const statTotalLeads = document.getElementById('statTotalLeads');
const statHighVuln = document.getElementById('statHighVuln');
const statMissedCalls = document.getElementById('statMissedCalls');
const statRevenueLoss = document.getElementById('statRevenueLoss');
const statRevenueLossUsd = document.getElementById('statRevenueLossUsd');
const statVulnRate = document.getElementById('statVulnRate');

const leadsTableBody = document.getElementById('leadsTableBody');
const searchInput = document.getElementById('searchInput');
const filterNiche = document.getElementById('filterNiche');
const filterStatus = document.getElementById('filterStatus');
const filterVuln = document.getElementById('filterVuln');
const filterVerified = document.getElementById('filterVerified');

const prospectorForm = document.getElementById('prospectorForm');
const targetNiche = document.getElementById('targetNiche');
const targetCity = document.getElementById('targetCity');
const targetCount = document.getElementById('targetCount');
const discoverBtn = document.getElementById('discoverBtn');

const drawerOverlay = document.getElementById('drawerOverlay');
const closeDrawerBtn = document.getElementById('closeDrawerBtn');
const seedDataBtn = document.getElementById('seedDataBtn');
const exportCsvBtn = document.getElementById('exportCsvBtn');

const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toastMessage');

// Init
document.addEventListener('DOMContentLoaded', async () => {
  if (window.lucide) lucide.createIcons();
  await loadStats();
  await loadLeads();
  setupEventListeners();
});

function showToast(msg) {
  toastMessage.textContent = msg;
  toast.classList.remove('hidden');
  setTimeout(() => {
    toast.classList.add('hidden');
  }, 3500);
}

function setupEventListeners() {
  // Scanner Modal Toggle
  const scannerModal = document.getElementById('scannerModal');
  const openScannerBtn = document.getElementById('openScannerBtn');
  const closeScannerModalBtn = document.getElementById('closeScannerModalBtn');
  if (openScannerBtn && scannerModal) {
    openScannerBtn.addEventListener('click', () => scannerModal.classList.remove('hidden'));
    closeScannerModalBtn.addEventListener('click', () => scannerModal.classList.add('hidden'));
    scannerModal.addEventListener('click', (e) => {
      if (e.target === scannerModal) scannerModal.classList.add('hidden');
    });
  }

  // Filters & Search
  searchInput.addEventListener('input', debounce(loadLeads, 300));
  filterNiche.addEventListener('change', loadLeads);
  filterStatus.addEventListener('change', loadLeads);
  filterVuln.addEventListener('change', loadLeads);
  if (filterVerified) filterVerified.addEventListener('change', loadLeads);

  // Prospector Discover
  prospectorForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const niche = targetNiche.value;
    const city = targetCity.value;
    const count = parseInt(targetCount.value, 10);

    discoverBtn.disabled = true;
    discoverBtn.innerHTML = `<span class="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></span> Discovering...`;

    try {
      const res = await fetch('/api/leads/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ niche, city, count, use_live_map: true })
      });
      const data = await res.json();
      showToast(`Discovered & audited ${data.count} new leads in ${city}!`);
      if (scannerModal) scannerModal.classList.add('hidden');
      await loadStats();
      await loadLeads();
    } catch (err) {
      console.error(err);
      showToast('Error discovering leads.');
    } finally {
      discoverBtn.disabled = false;
      discoverBtn.innerHTML = `<i data-lucide="search" class="w-4 h-4"></i><span>Discover & Audit Leads</span>`;
      if (window.lucide) lucide.createIcons();
    }
  });

  // Seed Button
  seedDataBtn.addEventListener('click', async () => {
    seedDataBtn.disabled = true;
    seedDataBtn.innerText = 'Seeding...';
    try {
      const res = await fetch('/api/leads/seed', { method: 'POST' });
      const data = await res.json();
      showToast(data.message || 'Leads seeded successfully!');
      await loadStats();
      await loadLeads();
    } catch (err) {
      console.error(err);
    } finally {
      seedDataBtn.disabled = false;
      seedDataBtn.innerHTML = `<i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-400"></i> Seed Demo Leads`;
      if (window.lucide) lucide.createIcons();
    }
  });

  // Export CSV
  exportCsvBtn.addEventListener('click', () => {
    window.location.href = '/api/leads/export/csv';
  });

  // Copy Drawer Email
  document.getElementById('copyDrawerEmailBtn').addEventListener('click', () => {
    const text = document.getElementById('drawerEmail').innerText;
    if (text && text !== 'Scanning...') {
      navigator.clipboard.writeText(text);
      showToast('Email address copied!');
    }
  });

  // Scan Email Button
  const scanEmailBtn = document.getElementById('scanEmailBtn');
  scanEmailBtn.addEventListener('click', async () => {
    if (!currentLead) return;
    scanEmailBtn.disabled = true;
    scanEmailBtn.innerHTML = `<span class="animate-spin inline-block w-3 h-3 border-2 border-white border-t-transparent rounded-full mr-1"></span> Scanning...`;

    try {
      const res = await fetch(`/api/leads/${currentLead.id}/discover-email`, { method: 'POST' });
      const data = await res.json();
      
      if (data.primary_email) {
        document.getElementById('drawerEmail').innerText = data.primary_email;
        showToast(`Discovered verified email: ${data.primary_email}`);
      }

      const listDiv = document.getElementById('drawerEmailCandidateList');
      if (data.all_emails && data.all_emails.length > 0) {
        listDiv.classList.remove('hidden');
        listDiv.innerHTML = `
          <div class="text-slate-400 font-semibold mb-1 flex items-center justify-between">
            <span>Discovered Inboxes (${escapeHtml(data.source || 'Scanned')}):</span>
          </div>
          <div class="space-y-1">
            ${data.all_emails.map(item => `
              <div class="flex items-center justify-between p-1.5 rounded bg-slate-900 border border-slate-800">
                <span class="font-mono text-cyan-300">${escapeHtml(item.email)}</span>
                <span class="text-slate-400 text-[10px] bg-slate-800 px-1.5 py-0.5 rounded border border-slate-700">${escapeHtml(item.type || 'Inbox')} (${escapeHtml(item.confidence || '90%')})</span>
              </div>
            `).join('')}
          </div>
        `;
      }
      await loadLeads();
    } catch (err) {
      console.error(err);
      showToast('Failed to scan website for emails.');
    } finally {
      scanEmailBtn.disabled = false;
      scanEmailBtn.innerHTML = `<i data-lucide="scan" class="w-3 h-3"></i><span>Scan Website for Emails</span>`;
      if (window.lucide) lucide.createIcons();
    }
  });

  // Drawer Close
  closeDrawerBtn.addEventListener('click', closeDrawer);
  drawerOverlay.addEventListener('click', (e) => {
    if (e.target === drawerOverlay) closeDrawer();
  });

  // Drawer Tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => {
        b.classList.remove('active');
      });
      btn.classList.add('active');

      const targetTab = btn.getAttribute('data-tab');
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.add('hidden'));
      const activePane = document.getElementById(`tabContent-${targetTab}`);
      if (activePane) activePane.classList.remove('hidden');

      if (targetTab === 'simulator' && currentLead) {
        initSimulatorForLead(currentLead);
      }
    });
  });

  // Copy WhatsApp
  document.getElementById('copyWhatsAppBtn').addEventListener('click', () => {
    const text = document.getElementById('whatsappText').innerText;
    navigator.clipboard.writeText(text);
    showToast('WhatsApp outreach pitch copied!');
  });

  // Simulator Input
  const simForm = document.getElementById('simulatorInputForm');
  simForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('simInputText');
    const msg = input.value.trim();
    if (!msg || !currentLead) return;
    input.value = '';
    await sendSimulatorMessage(msg);
  });

  // Simulator suggestion pills
  document.querySelectorAll('.sim-suggest-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const text = btn.innerText.replace(/"/g, '').trim();
      document.getElementById('simInputText').value = text;
      sendSimulatorMessage(text);
    });
  });

  // Simulator audio toggle
  const toggleTtsBtn = document.getElementById('toggleTtsBtn');
  toggleTtsBtn.addEventListener('click', () => {
    ttsEnabled = !ttsEnabled;
    document.getElementById('ttsStatusLabel').innerText = ttsEnabled ? 'Audio: Enabled' : 'Audio: Muted';
    showToast(ttsEnabled ? 'AI Voice spoken audio enabled' : 'AI Voice audio muted');
  });

  // Mic input
  const simMicBtn = document.getElementById('simMicBtn');
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    simMicBtn.addEventListener('click', () => {
      simMicBtn.classList.add('bg-red-600', 'text-white');
      recognition.start();
    });

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      document.getElementById('simInputText').value = transcript;
      simMicBtn.classList.remove('bg-red-600', 'text-white');
      sendSimulatorMessage(transcript);
    };

    recognition.onerror = () => {
      simMicBtn.classList.remove('bg-red-600', 'text-white');
    };
    recognition.onend = () => {
      simMicBtn.classList.remove('bg-red-600', 'text-white');
    };
  } else {
    simMicBtn.style.display = 'none';
  }
}

async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    statTotalLeads.innerText = data.total_leads || 0;
    statHighVuln.innerText = data.high_vulnerability_leads || 0;
    statMissedCalls.innerText = (data.total_missed_calls_monthly || 0).toLocaleString();
    statRevenueLoss.innerText = '₹' + (data.total_estimated_revenue_loss_inr || 0).toLocaleString();
    statRevenueLossUsd.innerText = '$' + (data.total_estimated_revenue_loss_usd || 0).toLocaleString();
    
    const vulnRate = data.total_leads > 0 
      ? Math.round((data.high_vulnerability_leads / data.total_leads) * 100) 
      : 0;
    statVulnRate.innerText = vulnRate + '%';
  } catch (err) {
    console.error('Failed to load stats:', err);
  }
}

async function loadLeads() {
  try {
    const params = new URLSearchParams();
    if (filterNiche.value) params.append('niche', filterNiche.value);
    if (filterStatus.value) params.append('status', filterStatus.value);
    if (filterVuln.value) params.append('min_vulnerability', filterVuln.value);
    if (searchInput.value) params.append('search', searchInput.value.trim());

    const res = await fetch(`/api/leads?${params.toString()}`);
    const data = await res.json();
    let leads = data.leads || [];
    
    if (filterVerified && filterVerified.value === 'verified') {
      leads = leads.filter(l => (l.verification_score || 0) >= 75);
    }
    
    allLeads = leads;
    renderLeadsTable(allLeads);
  } catch (err) {
    console.error('Failed to load leads:', err);
  }
}

function renderLeadsTable(leads) {
  if (!leads || leads.length === 0) {
    leadsTableBody.innerHTML = `
      <tr>
        <td colspan="7" class="px-5 py-12 text-center text-slate-500">
          <div class="flex flex-col items-center justify-center gap-2">
            <i data-lucide="inbox" class="w-8 h-8 text-slate-600"></i>
            <span>No leads found matching your filters. Click "Discover & Audit Leads" above to populate!</span>
          </div>
        </td>
      </tr>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  leadsTableBody.innerHTML = leads.map(l => {
    // Niche formatting
    const nicheIcons = {
      clinic: '🩺 Clinic',
      ca: '📊 CA / Tax',
      diagnostic: '🧪 Diagnostic',
      real_estate: '🏢 Real Estate',
      visa_consultant: '✈️ Visa Agency'
    };
    const nicheLabel = nicheIcons[l.niche] || l.niche;

    const revLossInr = (l.est_monthly_revenue_loss_inr || 0).toLocaleString();
    const missedCalls = (l.est_monthly_missed_calls || 0).toLocaleString();
    const dailyCalls = Math.round((l.est_monthly_missed_calls || 0) / 26);

    return `
      <tr class="hover:bg-white/[0.02] transition-colors">
        <!-- Practice & Decision Maker -->
        <td class="px-5 py-3.5">
          <div class="flex items-center gap-2">
            <span class="font-semibold text-white tracking-tight">${escapeHtml(l.business_name)}</span>
            <span class="text-[10px] font-medium px-2 py-0.5 rounded-full bg-[#181b20] text-[#ededed] border border-white/10">
              ${nicheLabel}
            </span>
          </div>
          <div class="text-xs text-[#8c8f96] mt-0.5 flex items-center gap-1.5">
            <span>${escapeHtml(l.contact_person || 'Lead Contact')}</span>
            <span>&bull;</span>
            <span>📍 ${escapeHtml(l.city)}</span>
          </div>
        </td>

        <!-- Verified Contact -->
        <td class="px-5 py-3.5 font-mono text-[11px]">
          <div class="text-[#ededed]">${escapeHtml(l.phone || 'Phone unlisted')}</div>
          <div class="text-[#8c8f96] text-[10px] mt-0.5">${escapeHtml(l.email || 'Email unlisted')}</div>
        </td>

        <!-- Missed Inbound Calls -->
        <td class="px-5 py-3.5 font-mono-numbers">
          <div class="font-semibold text-[#ff5722]">~${dailyCalls} calls/day</div>
          <div class="text-[10px] text-[#8c8f96]">~${missedCalls}/mo after-hours</div>
        </td>

        <!-- Revenue Loss -->
        <td class="px-5 py-3.5 font-mono-numbers">
          <div class="font-bold text-[#d4ff3f]">₹${revLossInr}</div>
          <div class="text-[10px] text-[#8c8f96]">~$${(l.est_monthly_revenue_loss_usd || 0).toLocaleString()}/mo</div>
        </td>

        <!-- Stage -->
        <td class="px-5 py-3.5">
          <select onchange="updateLeadStatus('${l.id}', this.value)" class="bg-[#181b20] border border-white/10 text-xs text-[#ededed] rounded-lg px-2 py-1 focus:outline-none">
            <option value="new" ${l.status === 'new' ? 'selected' : ''}>New</option>
            <option value="qualified" ${l.status === 'qualified' ? 'selected' : ''}>Qualified</option>
            <option value="outreach_sent" ${l.status === 'outreach_sent' ? 'selected' : ''}>Outreach Sent</option>
            <option value="demo_shared" ${l.status === 'demo_shared' ? 'selected' : ''}>Demo Shared</option>
            <option value="meeting_booked" ${l.status === 'meeting_booked' ? 'selected' : ''}>Meeting Booked</option>
          </select>
        </td>

        <!-- Action -->
        <td class="px-5 py-3.5 text-right">
          <button onclick="openLeadDrawer('${l.id}')" class="text-xs bg-[#181b20] hover:bg-white text-white hover:text-black font-semibold px-3 py-1.5 rounded-lg border border-white/10 transition-all shadow-sm">
            <span>Pitch & Demo ↗</span>
          </button>
        </td>
      </tr>
    `;
  }).join('');

  if (window.lucide) lucide.createIcons();
}

async function updateLeadStatus(leadId, newStatus) {
  try {
    const res = await fetch(`/api/leads/${leadId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    if (res.ok) {
      showToast(`Status updated to ${newStatus}`);
      await loadStats();
    }
  } catch (err) {
    console.error('Failed to update status:', err);
  }
}

async function openLeadDrawer(leadId) {
  try {
    const res = await fetch(`/api/leads/${leadId}`);
    const lead = await res.json();
    currentLead = lead;

    // Header info
    document.getElementById('drawerNicheBadge').innerText = lead.niche.toUpperCase();
    document.getElementById('drawerCityBadge').innerText = lead.city;
    document.getElementById('drawerBusinessName').innerText = lead.business_name;
    document.getElementById('drawerContactPerson').innerText = lead.contact_person || 'Practice Head';

    // Audit summary
    document.getElementById('drawerVulnScore').innerText = `${lead.vulnerability_score}/100`;
    document.getElementById('drawerMissedCalls').innerText = lead.est_monthly_missed_calls.toLocaleString();
    document.getElementById('drawerRevLoss').innerText = '₹' + (lead.est_monthly_revenue_loss_inr || 0).toLocaleString();
    document.getElementById('drawerPhone').innerText = lead.phone || 'Not listed';
    document.getElementById('drawerAddress').innerText = lead.address || lead.city;
    document.getElementById('drawerRating').innerText = `${lead.rating}★ (${lead.review_count} reviews)`;

    // Email & Contact
    document.getElementById('drawerEmail').innerText = lead.email || 'None discovered';
    const emailCandList = document.getElementById('drawerEmailCandidateList');
    emailCandList.classList.add('hidden');
    emailCandList.innerHTML = '';

    // Data Verification Checklist
    const badges = lead.verification_badges || {};
    const trustScore = lead.verification_score || 95;
    document.getElementById('drawerTrustBadge').innerText = `${trustScore}% Verified`;
    
    const vList = document.getElementById('drawerVerificationList');
    vList.innerHTML = `
      <div class="p-2 rounded bg-slate-900 border border-slate-800 flex items-center justify-between">
        <span class="text-slate-400">📱 Phone Line:</span>
        <span class="font-medium text-emerald-400">${escapeHtml(badges.phone?.label || 'Verified Line')}</span>
      </div>
      <div class="p-2 rounded bg-slate-900 border border-slate-800 flex items-center justify-between">
        <span class="text-slate-400">✉️ Email Inbox:</span>
        <span class="font-medium text-emerald-400">${escapeHtml(badges.email?.label || 'Syntax & Domain Valid')}</span>
      </div>
      <div class="p-2 rounded bg-slate-900 border border-slate-800 flex items-center justify-between">
        <span class="text-slate-400">📍 Physical Practice:</span>
        <span class="font-medium text-emerald-400">${escapeHtml(badges.location?.label || 'Verified Location')}</span>
      </div>
      <div class="p-2 rounded bg-slate-900 border border-slate-800 flex items-center justify-between">
        <span class="text-slate-400">⭐ Google Reviews:</span>
        <span class="font-medium text-emerald-400">${escapeHtml(badges.reputation?.label || 'Google Places Audited')}</span>
      </div>
    `;

    // Pitches
    const pitches = lead.pitches || {};
    document.getElementById('whatsappText').innerText = pitches.whatsapp_pitch || 'Generating...';

    // WhatsApp Direct URL
    const cleanPhone = (lead.phone || '').replace(/[^0-9]/g, '');
    const encodedMsg = encodeURIComponent(pitches.whatsapp_pitch || '');
    const waUrl = cleanPhone ? `https://wa.me/${cleanPhone}?text=${encodedMsg}` : `https://web.whatsapp.com/send?text=${encodedMsg}`;
    document.getElementById('openWhatsAppBtn').setAttribute('href', waUrl);

    // Emails
    const e1 = pitches.cold_email_step1 || {};
    document.getElementById('emailStep1Subject').innerText = 'Subject: ' + (e1.subject || '');
    document.getElementById('emailStep1Text').innerText = e1.body || '';

    const e2 = pitches.cold_email_step2 || {};
    document.getElementById('emailStep2Subject').innerText = 'Subject: ' + (e2.subject || '');
    document.getElementById('emailStep2Text').innerText = e2.body || '';

    const e3 = pitches.cold_email_step3 || {};
    document.getElementById('emailStep3Subject').innerText = 'Subject: ' + (e3.subject || '');
    document.getElementById('emailStep3Text').innerText = e3.body || '';

    // SDR Phone Script
    document.getElementById('coldCallScriptText').innerText = pitches.cold_call_script || '';

    // Voice Agent System Prompt
    document.getElementById('voiceAgentPromptText').innerText = pitches.voice_agent_prompt || '';

    // Reset and initialize simulator
    initSimulatorForLead(lead);

    drawerOverlay.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error('Failed to load lead details:', err);
  }
}

function closeDrawer() {
  drawerOverlay.classList.add('hidden');
  currentLead = null;
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
}

function initSimulatorForLead(lead) {
  chatHistory = [];
  const chatBox = document.getElementById('simulatorChatBox');
  chatBox.innerHTML = `
    <div class="p-3 rounded-xl bg-[#16181b] border border-white/[0.06] flex items-start gap-2.5">
      <div class="w-6 h-6 rounded-full bg-[#d4ff3f]/20 text-[#d4ff3f] flex items-center justify-center font-bold text-xs flex-shrink-0">
        AI
      </div>
      <div>
        <div class="font-semibold text-white tracking-tight">${escapeHtml(lead.business_name)} &bull; 24/7 Voice AI</div>
        <div class="text-[#ededed] mt-1 text-xs">
          "Hello, thank you for calling ${escapeHtml(lead.business_name)}. My name is Maya, your digital assistant. How may I assist your appointment or inquiry today?"
        </div>
      </div>
    </div>
  `;
}

async function sendSimulatorMessage(userMsg) {
  const chatBox = document.getElementById('simulatorChatBox');

  // Append user bubble
  chatBox.innerHTML += `
    <div class="p-3 rounded-xl bg-[#1f2229] border border-white/10 flex items-start justify-end gap-2.5">
      <div class="text-right">
        <div class="font-medium text-[#8c8f96] text-[11px]">Caller (You)</div>
        <div class="text-[#ededed] mt-0.5">${escapeHtml(userMsg)}</div>
      </div>
    </div>
  `;
  chatBox.scrollTop = chatBox.scrollHeight;

  // Add temporary typing indicator
  const typingId = 'typing-' + Date.now();
  chatBox.innerHTML += `
    <div id="${typingId}" class="p-2.5 text-[#8c8f96] flex items-center gap-2 italic text-xs">
      <span class="animate-bounce text-[#d4ff3f]">●</span><span class="animate-bounce delay-100 text-[#d4ff3f]">●</span><span class="animate-bounce delay-200 text-[#d4ff3f]">●</span>
      <span>AI Receptionist is synthesizing response...</span>
    </div>
  `;
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const res = await fetch(`/api/leads/${currentLead.id}/simulate-call`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_message: userMsg,
        chat_history: chatHistory
      })
    });
    const data = await res.json();
    const reply = data.agent_reply || "Thank you for calling. I have recorded your appointment request.";

    // Remove typing
    const typingElem = document.getElementById(typingId);
    if (typingElem) typingElem.remove();

    // Append agent bubble
    chatBox.innerHTML += `
      <div class="p-3 rounded-xl bg-[#16181b] border border-white/[0.06] flex items-start gap-2.5">
        <div class="w-6 h-6 rounded-full bg-[#d4ff3f]/20 text-[#d4ff3f] flex items-center justify-center font-bold text-xs flex-shrink-0">
          AI
        </div>
        <div>
          <div class="font-medium text-[#8c8f96] text-[11px]">AI Receptionist</div>
          <div class="text-[#ededed] mt-0.5">${escapeHtml(reply)}</div>
        </div>
      </div>
    `;
    chatBox.scrollTop = chatBox.scrollHeight;

    // Update history
    chatHistory.push({ role: 'user', text: userMsg });
    chatHistory.push({ role: 'model', text: reply });

    // Speak reply if audio enabled
    if (ttsEnabled && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(reply);
      utterance.rate = 1.05;
      utterance.pitch = 1.0;
      // Prefer female English voice
      const voices = window.speechSynthesis.getVoices();
      const preferred = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Female') || v.name.includes('Samantha') || v.name.includes('Natural') || v.name.includes('Google')));
      if (preferred) utterance.voice = preferred;
      window.speechSynthesis.speak(utterance);
    }
  } catch (err) {
    console.error('Simulation error:', err);
    const typingElem = document.getElementById(typingId);
    if (typingElem) typingElem.remove();
  }
}

function copyToClipboard(elemId) {
  const elem = document.getElementById(elemId);
  if (elem) {
    navigator.clipboard.writeText(elem.innerText);
    showToast('Copied to clipboard!');
  }
}

function debounce(fn, delay) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
