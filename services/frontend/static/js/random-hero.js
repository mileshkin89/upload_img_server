/**
 * @file random-hero.js
 * @description
 * Sets a random background image for the `.hero-image` element
 * from a predefined set of images upon DOM content load.
 */

/**
 * Event listener for DOMContentLoaded.
 * Selects a random image from `/static/random_images/1.png` to `5.png`
 * and applies it as the background of the `.hero-image` element.
 */
window.addEventListener('DOMContentLoaded', () => {
  const heroImage = document.querySelector('.hero-image');

  const randomNumber = Math.floor(Math.random() * 5) + 1;

  const imagePath = `/static/random_images/${randomNumber}.png`;

  heroImage.style.backgroundImage = `url('${imagePath}')`;
});
