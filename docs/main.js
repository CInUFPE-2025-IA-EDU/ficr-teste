console.log('ficr-teste iniciado');
function formatarMoeda(v){ return new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(v); }
function validarEmail(e){ return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e); }
document.addEventListener('DOMContentLoaded',()=>{ const app=document.getElementById('app'); if(app){ const p=document.createElement('p'); p.textContent='Dica: rode "npm run check" antes do PR.'; app.appendChild(p); }});

