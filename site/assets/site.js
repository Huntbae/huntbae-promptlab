/* huntbae.com shared script — topbar, footer, reveal, helpers */
(function(){
  'use strict';
  var SITE='https://www.huntbae.com';
  var LINKS={
    home:SITE+'/main', services:SITE+'/services', gov:SITE+'/gov-support', areas:SITE+'/services/all',
    talks:SITE+'/talks', community:SITE+'/community', library:SITE+'/library', prompt:SITE+'/library/prompt-lab',
    mobility:SITE+'/mobility', about:SITE+'/about',
    diag:'https://forms.gle/ULVEKNKtoLuwAPKq9', member:'https://forms.gle/GNgbYhEbgsZnZ8yV9', mail:'mailto:huntbae@huntbae.com'
  };
  window.HB={LINKS:LINKS,SITE:SITE};
  // Google Sites 삽입 블록은 너비에 비례해 높이가 정해지므로, 데스크톱에서는 1154px 기준으로 확대·축소한다
  var embedded=(function(){try{return window.self!==window.top}catch(e){return true}})();
  function fit(){var d=document.documentElement,w=window.innerWidth,z=1;if(embedded&&w>760){z=w/1154;d.style.zoom=z.toFixed(4);d.classList.add('dz')}else{d.style.zoom='';d.classList.remove('dz')}if(document.body)document.body.style.minHeight=embedded?Math.floor(window.innerHeight/z)+'px':''}
  document.addEventListener('DOMContentLoaded',fit);
  fit();window.addEventListener('resize',fit);
  var NAMES={home:'홈',services:'서비스',gov:'정부지원사업',areas:'업무 영역',talks:'강연·자문',community:'커뮤니티',library:'자료실',mobility:'모빌리티',about:'About·문의'};

  function topbar(){
    var el=document.querySelector('[data-topbar]'); if(!el) return;
    var key=document.body.dataset.page||'home', trail=(el.dataset.topbar||'').split('/').filter(Boolean);
    var crumb='<a href="'+LINKS.home+'" target="_top">HOME</a>'+trail.map(function(k){return ' <span>/</span> '+(k===key?'<b>'+(NAMES[k]||k)+'</b>':'<a href="'+(LINKS[k]||'#')+'" target="_top">'+(NAMES[k]||k)+'</a>')}).join('');
    el.innerHTML='<div class="wrap"><div class="crumb">'+crumb+'</div><div class="sp"><a href="'+LINKS.gov+'" target="_top">진행 중 공고</a><a href="'+LINKS.services+'" target="_top">서비스·가격</a><a class="btn btn-gold btn-sm" href="'+LINKS.diag+'" target="_blank" rel="noopener">무료 AI 진단</a></div></div>';
  }
  function footer(){
    var el=document.querySelector('[data-footer]'); if(!el) return;
    el.innerHTML='<div class="wrap"><div><b>클랜헌트 유한회사</b> · 대표 배효수 · 사업자등록번호 687-81-03346 · 통신판매업신고 제 2026-경남진주-0081호<br>경상남도 진주시 신평공원길75번길 14-1, 2층 · 전화 010-8881-3760 · <a href="'+LINKS.mail+'">huntbae@huntbae.com</a></div><div>© Hunt Bae, Since 2005 · <a href="https://www.clanhunts.kr" target="_blank" rel="noopener">clanhunts.kr</a></div></div>';
  }
  function reveal(){
    var els=[].slice.call(document.querySelectorAll('.rv'));
    if(!('IntersectionObserver' in window)){els.forEach(function(e){e.classList.add('in')});return}
    var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target)}})},{threshold:.12});
    els.forEach(function(e){io.observe(e)});
  }
  function links(){
    // 사이트 내부 링크는 Google Sites 상위 창에서 열리도록
    [].slice.call(document.querySelectorAll('a[href^="'+SITE+'"]')).forEach(function(a){if(!a.target)a.target='_top'});
    [].slice.call(document.querySelectorAll('a[href^="http"]:not([href^="'+SITE+'"])')).forEach(function(a){if(!a.target){a.target='_blank';a.rel='noopener'}});
    [].slice.call(document.querySelectorAll('[data-link]')).forEach(function(a){var k=a.dataset.link;if(LINKS[k]){a.href=LINKS[k];a.target=/^https?:\/\/forms|mailto/.test(LINKS[k])?'_blank':'_top'}});
  }
  var tt;window.toast=function(m){var t=document.querySelector('.toast');if(!t){t=document.createElement('div');t.className='toast';document.body.appendChild(t)}t.textContent=m;t.classList.add('on');clearTimeout(tt);tt=setTimeout(function(){t.classList.remove('on')},2200)};
  document.addEventListener('DOMContentLoaded',function(){topbar();footer();links();reveal()});
})();
