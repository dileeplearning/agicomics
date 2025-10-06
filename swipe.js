(function(){
  var startX=0,startY=0,startT=0,tracking=false,canceled=false;
  function isInteractive(el){ if(!el) return false; var tag=el.tagName?el.tagName.toLowerCase():''; if(tag==='input'||tag==='textarea'||tag==='select'||tag==='button') return true; if(el.closest && (el.closest('.search')||el.closest('.dd'))) return true; return false; }
  document.addEventListener('touchstart', function(e){ if(!e.touches||e.touches.length!==1) return; var t=e.touches[0]; if(isInteractive(e.target)) return; startX=t.clientX; startY=t.clientY; startT=Date.now(); tracking=true; canceled=false; }, { passive:true });
  document.addEventListener('touchmove', function(e){ if(!tracking||canceled||!e.touches||e.touches.length!==1) return; var t=e.touches[0]; var dy=Math.abs(t.clientY-startY); if(dy>30){ canceled=true; } }, { passive:true });
  document.addEventListener('touchend', function(e){ if(!tracking||canceled){ tracking=false; return; } var dt=Date.now()-startT; if(dt>1000){ tracking=false; return; } var ch=e.changedTouches && e.changedTouches[0]; var endX=ch?ch.clientX:startX; var dx=endX-startX; var prev=document.querySelector('a.nav-btn.prev')||document.querySelector('a[rel="prev"]'); var next=document.querySelector('a.nav-btn.next')||document.querySelector('a[rel="next"]'); if(dx<=-50 && next){ window.location.href=next.getAttribute('href'); } else if(dx>=50 && prev){ window.location.href=prev.getAttribute('href'); } tracking=false; }, { passive:true });
  document.addEventListener('touchcancel', function(){ tracking=false; }, { passive:true });
})();
