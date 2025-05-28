const swiper = new Swiper(".mySwiper", {
  loop: true,
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
    dynamicBullets: true
  },
  effect: 'fade',
  speed: 700,
  autoplay: {
    delay: 4000,
    disableOnInteraction: false
  }
});
