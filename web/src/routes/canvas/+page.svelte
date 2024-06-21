<script lang="ts">
  import { onMount } from 'svelte';
  import { fabric } from 'fabric';
  import type { IDataURLOptions } from 'fabric/fabric-impl';
  import { jsPDF } from 'jspdf';

  let canvas: fabric.Canvas;
  let img: fabric.Image;

  onMount(() => {
    canvas = new fabric.Canvas('c');
  });

  function loadImage(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;
    const file = input.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      if (!e.target?.result) return;
      fabric.Image.fromURL(e.target?.result?.toString(), (image) => {
        img = image;
        if (!img || !img.width || !img.height ) return;
        const scaleX = canvas.getWidth() / img.width;
        const scaleY = canvas.getHeight() / img.height;
        const scaleToFit = Math.min(scaleX, scaleY)
        img.scaleToWidth(img.width * scaleToFit);
        img.scaleToHeight(img.height * scaleToFit);
        canvas.clear();
        canvas.add(img);
        canvas.renderAll();
      });
    };
    reader.readAsDataURL(file);
  }

  function saveAsPDF() {
    // Canvas에 이미지가 없으면 alert
    if (!img) {
      alert('Please load an image first');
      return;
    }
    const pdfWidth = 210;
    const pdfHeight = 297;
    const imgData = canvas.toDataURL("image/png" as IDataURLOptions);

    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: [pdfWidth, pdfHeight],
    });
    pdf.addImage(imgData, "PNG", 0, 0, pdfWidth, pdfHeight);
    pdf.save("download.pdf");
  }

  function applyFilter(index: number, filter: fabric.IBaseFilter) {
    if (!img.filters) return;
    img.filters[index] = filter;
    img.applyFilters();
    canvas.renderAll();
  }

  function adjustSaturation(value: number) {
    applyFilter(0, new fabric.Image.filters.Saturation({ saturation: value }));
  }

  function adjustExposure(value: number) {
    applyFilter(1, new fabric.Image.filters.Brightness({ brightness: value }));
  }

  function adjustContrast(value: number) {
    applyFilter(2, new fabric.Image.filters.Contrast({ contrast: value }));
  }
</script>

<style>
  canvas {
    border: 1px solid #ccc;
  }
</style>

<main>
  <div class="flex mt-10">
  <div>
    <canvas id="c" width="500" height="707"></canvas>
  </div>
  <div class="ml-10">
    <div>
      <h1>Fabric.js adjustments example</h1>
    </div>
    <div style="margin-top: 20px;">
      <input type="file" accept="image/*" on:change="{loadImage}">
    </div>
    <div>
      <!-- svelte-ignore a11y-label-has-associated-control -->
      <label>Saturation: </label>
      <input type="range" min="-1" max="1" step="0.1" on:input="{(e) => {
        if (e.target instanceof HTMLInputElement) adjustSaturation(parseFloat(e.target.value))
      }}">
    </div>
    <div>
      <!-- svelte-ignore a11y-label-has-associated-control -->
      <label>Exposure: </label>
      <input type="range" min="-1" max="1" step="0.1" on:input="{(e) => {
        if (e.target instanceof HTMLInputElement) adjustExposure(parseFloat(e.target.value))
      }}">
    </div>
    <div>
      <!-- svelte-ignore a11y-label-has-associated-control -->
      <label>Contrast: </label>
      <input type="range" min="-1" max="1" step="0.1" on:input="{(e) => {
        if (e.target instanceof HTMLInputElement)
        adjustContrast(parseFloat(e.target.value))
      }}">
    </div>
    <hr>
    <div class="pt-10">
      <button on:click="{saveAsPDF}">Save as PDF</button>
    </div>
  </div>
</div>
</main>
