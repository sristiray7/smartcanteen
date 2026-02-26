let cart = JSON.parse(localStorage.getItem("cart")) || [];
let activeItem = null;

function addCurrentToCart() {
  if (!activeItem) return;

  cart.push(activeItem);
  localStorage.setItem("cart", JSON.stringify(cart));
  document.getElementById("cart-count").innerText = cart.length;
}

function goToDashboard() {
  window.location.href = "dashboard.html";
}
const foods = [
  {
    id:1,
    name:"Burger",
    price:50,
    image:"assets/images/burger.png",
    gradient:"linear-gradient(135deg, #ff4e50, #f9d423)"
  },
  {
    id:2,
    name:"Pizza",
    price:120,
    image:"assets/images/pizza.png",
    gradient:"linear-gradient(135deg, #f12711, #f5af19)"
  }
];

const carousel = document.getElementById("carousel");
const background = document.getElementById("background");
const foodName = document.getElementById("food-name");

let rotationY = 0;
let activeIndex = 0;

const count = foods.length;
const anglePerItem = 360 / count;
const radius = 700;

foods.forEach((food, i) => {
  const angle = i * anglePerItem;

  const div = document.createElement("div");
  div.className = "item";
  div.style.transform = `rotateY(${angle}deg) translateZ(${radius}px)`;

  const img = document.createElement("img");
  img.src = food.image;

  div.appendChild(img);
  carousel.appendChild(div);
});

function updateActive() {
  const index = Math.round(-rotationY / anglePerItem);
  activeIndex = ((index % count) + count) % count;

  activeItem = foods[activeIndex];
  foodName.innerText = activeItem.name;
  background.style.background = activeItem.gradient;
}

updateActive();

window.addEventListener("wheel", (e) => {
  rotationY += e.deltaY * 0.15;
  carousel.style.transform = `rotateY(${rotationY}deg)`;
  updateActive();
});
