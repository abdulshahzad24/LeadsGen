// State
let allLeads = [];
let currentLead = null;
let chatHistory = [];
let ttsEnabled = true;

// DOM Elements
const statTotalLeads = document.getElementById('statTotalLeads');
const statMissedCalls = document.getElementById('statMissedCalls');
const statRevenueLoss = document.getElementById('statRevenueLoss');

const leadsTableBody = document.getElementById('leadsTableBody');
const searchInput = document.getElementById('searchInput');
const filterNiche = document.getElementById('filterNiche');
const filterStatus = document.getElementById('filterStatus');

const scannerModal = document.getElementById('scannerModal');
const openScannerBtn = document.getElementById('openScannerBtn');
const closeScannerModalBtn = document.getElementById('closeScannerModalBtn');

const prospectorForm = document.getElementById('prospectorForm');
const targetNiche = document.getElementById('targetNiche');
const targetCity = document.getElementById('targetCity');
const targetCount = document.getElementById('targetCount');
const discoverBtn = document.getElementById('discoverBtn');

const drawerOverlay = document.getElementById('drawerOverlay');
const closeDrawerBtn = document.getElementById('closeDrawerBtn');
const exportCsvBtn = document.getElementById('exportCsvBtn');

const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toastMessage');

// Init
document.addEventListener('DOMContentLoaded', async () => {
  if (window.lucide) lucide.createIcons();
  setupEventListeners();
  await loadStats();
  await loadLeads();
});

function showToast(msg) {
  if (!toast || !toastMessage) return;
  toastMessage.textContent = msg;
  toast.classList.remove('hidden');
  setTimeout(() => {
    toast.classList.add('hidden');
  }, 3500);
}

function setupEventListeners() {
  // Scanner Modal Open/Close
  if (openScannerBtn && scannerModal) {
    openScannerBtn.addEventListener('click', () => {
      scannerModal.classList.remove('hidden');
    });
  }
  if (closeScannerModalBtn && scannerModal) {
    closeScannerModalBtn.addEventListener('click', () => {
      scannerModal.classList.add('hidden');
    });
  }
  if (scannerModal) {
    scannerModal.addEventListener('click', (e) => {
      if (e.target === scannerModal) scannerModal.classList.add('hidden');
    });
  }

  // Filters & Search
  if (searchInput) {
    searchInput.addEventListener('input', debounce(loadLeads, 250));
  }
  if (filterNiche) {
    filterNiche.addEventListener('change', loadLeads);
  }
  if (filterStatus) {
    filterStatus.addEventListener('change', loadLeads);
  }

  // Prospector Discover Form
  if (prospectorForm) {
    prospectorForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const niche = targetNiche ? targetNiche.value : 'clinic';
      const city = targetCity ? targetCity.value : 'Mumbai';
      const count = targetCount ? parseInt(targetCount.value, 10) : 5;

      if (discoverBtn) {
        discoverBtn.disabled = true;
        discoverBtn.innerHTML = `<span class="animate-spin inline-block w-3.5 h-3.5 border-2 border-black border-t-transparent rounded-full mr-1.5"></span> Finding Leads...`;
      }

      try {
        const res = await fetch('/api/leads/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ niche, city, count, use_live_map: false })
        });
        const data = await res.json();
        const found = data.count || (data.leads ? data.leads.length : 0);
        showToast(`Discovered & audited ${found} new leads in ${city}!`);
        
        if (scannerModal) {
          scannerModal.classList.add('hidden');
        }
        await loadStats();
        await loadLeads();
      } catch (err) {
        console.error('Error discovering leads:', err);
        showToast('Error finding leads.');
      } finally {
        if (discoverBtn) {
          discoverBtn.disabled = false;
          discoverBtn.innerHTML = `<i data-lucide="search" class="w-3.5 h-3.5"></i><span>Scan & Audit Leads</span>`;
          if (window.lucide) lucide.createIcons();
        }
      }
    });
  }

  // Export CSV
  if (exportCsvBtn) {
    exportCsvBtn.addEventListener('click', () => {
      window.location.href = '/api/leads/export/csv';
    });
  }

  // Drawer Close
  if (closeDrawerBtn) {
    closeDrawerBtn.addEventListener('click', closeDrawer);
  }
  if (drawerOverlay) {
    drawerOverlay.addEventListener('click', (e) => {
      if (e.target === drawerOverlay) closeDrawer();
    });
  }

  // Drawer Tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
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
  const copyWhatsAppBtn = document.getElementById('copyWhatsAppBtn');
  if (copyWhatsAppBtn) {
    copyWhatsAppBtn.addEventListener('click', () => {
      const waText = document.getElementById('whatsappText');
      if (waText) {
        navigator.clipboard.writeText(waText.innerText);
        showToast('WhatsApp hook copied!');
      }
    });
  }

  // Simulator Input Form
  const simForm = document.getElementById('simulatorInputForm');
  if (simForm) {
    simForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = document.getElementById('simInputText');
      if (!input) return;
      const msg = input.value.trim();
      if (!msg || !currentLead) return;
      input.value = '';
      await sendSimulatorMessage(msg);
    });
  }

  // Simulator quick suggestion pills
  document.querySelectorAll('.sim-suggest-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const text = btn.innerText.replace(/"/g, '').trim();
      const input = document.getElementById('simInputText');
      if (input) input.value = text;
      sendSimulatorMessage(text);
    });
  });

  // Simulator Audio Toggle
  const toggleTtsBtn = document.getElementById('toggleTtsBtn');
  if (toggleTtsBtn) {
    toggleTtsBtn.addEventListener('click', () => {
      ttsEnabled = !ttsEnabled;
      const label = document.getElementById('ttsStatusLabel');
      if (label) label.innerText = ttsEnabled ? 'Audio: On' : 'Audio: Muted';
      showToast(ttsEnabled ? 'Spoken audio enabled' : 'Audio muted');
    });
  }
}

async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    if (statTotalLeads) statTotalLeads.innerText = data.total_leads || 0;
    if (statMissedCalls) statMissedCalls.innerText = (data.total_missed_calls_monthly || 0).toLocaleString();
    if (statRevenueLoss) statRevenueLoss.innerText = '₹' + (data.total_estimated_revenue_loss_inr || 0).toLocaleString();
  } catch (err) {
    console.error('Failed to load stats:', err);
  }
}

async function loadLeads() {
  try {
    const params = new URLSearchParams();
    if (filterNiche && filterNiche.value) params.append('niche', filterNiche.value);
    if (filterStatus && filterStatus.value) params.append('status', filterStatus.value);
    if (searchInput && searchInput.value.trim()) params.append('search', searchInput.value.trim());

    const res = await fetch(`/api/leads?${params.toString()}`);
    const data = await res.json();
    allLeads = data.leads || [];
    renderLeadsTable(allLeads);
  } catch (err) {
    console.error('Failed to load leads:', err);
  }
}

function renderLeadsTable(leads) {
  if (!leadsTableBody) return;

  if (!leads || leads.length === 0) {
    leadsTableBody.innerHTML = `
      <tr>
        <td colspan="6" class="px-5 py-12 text-center text-[#52545a]">
          <div class="flex flex-col items-center justify-center gap-2">
            <i data-lucide="inbox" class="w-6 h-6 text-[#52545a]"></i>
            <span>No leads found matching your search. Click "Find Leads" above to scan practices!</span>
          </div>
        </td>
      </tr>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  const nicheIcons = {
    clinic: '🩺 Clinic',
    ca: '📊 CA / Tax',
    diagnostic: '🧪 Diagnostic',
    real_estate: '🏢 Real Estate',
    visa_consultant: '✈️ Visa Agency'
  };

  leadsTableBody.innerHTML = leads.map(l => {
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
            <span>${escapeHtml(l.contact_person || 'Practice Head')}</span>
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
    const nicheBadge = document.getElementById('drawerNicheBadge');
    if (nicheBadge) nicheBadge.innerText = (lead.niche || 'CLINIC').toUpperCase();
    
    const cityBadge = document.getElementById('drawerCityBadge');
    if (cityBadge) cityBadge.innerText = lead.city || '';

    const trustBadge = document.getElementById('drawerTrustBadge');
    if (trustBadge) trustBadge.innerText = `${lead.verification_score || 95}% Verified`;

    const busName = document.getElementById('drawerBusinessName');
    if (busName) busName.innerText = lead.business_name || '';

    const contactName = document.getElementById('drawerContactPerson');
    if (contactName) contactName.innerText = lead.contact_person || 'Practice Head';

    // Metric Summary
    const missedElem = document.getElementById('drawerMissedCalls');
    if (missedElem) missedElem.innerText = Math.round((lead.est_monthly_missed_calls || 0) / 26);

    const revElem = document.getElementById('drawerRevLoss');
    if (revElem) revElem.innerText = '₹' + (lead.est_monthly_revenue_loss_inr || 0).toLocaleString();

    const phoneElem = document.getElementById('drawerPhone');
    if (phoneElem) phoneElem.innerText = `${lead.phone || 'No phone'} • ${lead.email || ''}`;

    // Pitches
    const pitches = lead.pitches || {};
    const waText = document.getElementById('whatsappText');
    if (waText) waText.innerText = pitches.whatsapp_pitch || '';

    // WhatsApp Direct link
    const cleanPhone = (lead.phone || '').replace(/[^0-9]/g, '');
    const encodedMsg = encodeURIComponent(pitches.whatsapp_pitch || '');
    const waUrl = cleanPhone 
      ? `https://wa.me/${cleanPhone}?text=${encodedMsg}` 
      : `https://web.whatsapp.com/send?text=${encodedMsg}`;
    const openWaBtn = document.getElementById('openWhatsAppBtn');
    if (openWaBtn) openWaBtn.setAttribute('href', waUrl);

    // Email
    const e1 = pitches.cold_email_step1 || {};
    const emailSubj = document.getElementById('emailStep1Subject');
    if (emailSubj) emailSubj.innerText = 'Subject: ' + (e1.subject || '');
    const emailBody = document.getElementById('emailStep1Text');
    if (emailBody) emailBody.innerText = e1.body || '';

    // Init simulator
    initSimulatorForLead(lead);

    if (drawerOverlay) drawerOverlay.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error('Failed to load lead details:', err);
  }
}

function closeDrawer() {
  if (drawerOverlay) drawerOverlay.classList.add('hidden');
  currentLead = null;
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
}

function initSimulatorForLead(lead) {
  chatHistory = [];
  const chatBox = document.getElementById('simulatorChatBox');
  if (!chatBox) return;

  chatBox.innerHTML = `
    <div class="p-2.5 rounded-xl bg-[#16181b] border border-white/[0.06] flex items-start gap-2">
      <div class="w-5 h-5 rounded-full bg-[#d4ff3f]/20 text-[#d4ff3f] flex items-center justify-center font-bold text-[10px] flex-shrink-0">
        AI
      </div>
      <div>
        <div class="font-semibold text-white tracking-tight text-xs">${escapeHtml(lead.business_name)} &bull; 24/7 Voice AI</div>
        <div class="text-[#ededed] mt-0.5 text-xs">
          "Hello, thank you for calling ${escapeHtml(lead.business_name)}. My name is Maya, your digital assistant. How may I assist your appointment or inquiry today?"
        </div>
      </div>
    </div>
  `;
}

async function sendSimulatorMessage(userMsg) {
  const chatBox = document.getElementById('simulatorChatBox');
  if (!chatBox) return;

  chatBox.innerHTML += `
    <div class="p-2.5 rounded-xl bg-[#1f2229] border border-white/10 flex items-start justify-end gap-2">
      <div class="text-right">
        <div class="font-medium text-[#8c8f96] text-[10px]">Caller (You)</div>
        <div class="text-[#ededed] mt-0.5 text-xs">${escapeHtml(userMsg)}</div>
      </div>
    </div>
  `;
  chatBox.scrollTop = chatBox.scrollHeight;

  const typingId = 'typing-' + Date.now();
  chatBox.innerHTML += `
    <div id="${typingId}" class="p-2 text-[#8c8f96] flex items-center gap-1.5 italic text-[11px]">
      <span class="animate-bounce text-[#d4ff3f]">●</span><span class="animate-bounce delay-100 text-[#d4ff3f]">●</span><span class="animate-bounce delay-200 text-[#d4ff3f]">●</span>
      <span>AI Receptionist is replying...</span>
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

    const typingElem = document.getElementById(typingId);
    if (typingElem) typingElem.remove();

    chatBox.innerHTML += `
      <div class="p-2.5 rounded-xl bg-[#16181b] border border-white/[0.06] flex items-start gap-2">
        <div class="w-5 h-5 rounded-full bg-[#d4ff3f]/20 text-[#d4ff3f] flex items-center justify-center font-bold text-[10px] flex-shrink-0">
          AI
        </div>
        <div>
          <div class="font-medium text-[#8c8f96] text-[10px]">AI Receptionist</div>
          <div class="text-[#ededed] mt-0.5 text-xs">${escapeHtml(reply)}</div>
        </div>
      </div>
    `;
    chatBox.scrollTop = chatBox.scrollHeight;

    chatHistory.push({ role: 'user', text: userMsg });
    chatHistory.push({ role: 'model', text: reply });

    if (ttsEnabled && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(reply);
      utterance.rate = 1.05;
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
