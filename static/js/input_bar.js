class InputBar {
  constructor(parent_element) {
    this.root = parent_element;
    this.input_bar = document.createElement("div");
    this.input_bar.innerHMTL = ``;
    this.root.appendChild(this.input_bar);
  }
}