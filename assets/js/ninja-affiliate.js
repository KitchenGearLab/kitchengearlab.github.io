/* Only Ninja collection CTAs emit this event. Existing analytics configuration is unchanged. */
(()=>{if(window.kglNinjaAffiliateBound)return;window.kglNinjaAffiliateBound=true;
document.addEventListener("click",event=>{const a=event.target.closest?.("a[data-affiliate-product]");
if(!a||typeof window.gtag!=="function")return;
window.gtag("event","affiliate_click",{product_id:a.dataset.affiliateProduct,asin:a.dataset.asin,placement:a.dataset.placement,link_url:a.href,transport_type:"beacon"});
});})();
