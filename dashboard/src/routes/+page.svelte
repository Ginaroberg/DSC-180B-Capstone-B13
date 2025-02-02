<script lang="ts">
    import mapboxgl from 'mapbox-gl';
    import 'mapbox-gl/dist/mapbox-gl.css';
    import { onMount, onDestroy } from 'svelte';

    let map: mapboxgl.Map;
    let mapContainer: HTMLElement;
    let selectedCoordinates = { lat: 0, lon: 0 };
    let loading = true;
    let errorMessage = '';
    let climateData = [];
    let timeIndex = 0; 
    let plotUrl = ''; 
    let selectedCrop = ''; 
    let crops = ['mai', 'ri1', 'ri2', 'soy', 'swh', 'wwh']; 

    const MAPBOX_ACCESS_TOKEN = 'your-mapbox-access-token';

    async function fetchClimateData() {
        try {
            const response = await fetch('http://127.0.0.1:8000/climate-data'); // Update with your FastAPI endpoint
            if (!response.ok) throw new Error("Failed to fetch climate data");
            climateData = await response.json(); // Store data in climateData
            loading = false;
        } catch (error) {
            errorMessage = error.message;
            loading = false;
        }
    }

    async function generatePlot() {
        try {
            const response = await fetch(`http://127.0.0.1:8000/generate-plot?time_index=${timeIndex}&crop=${selectedCrop}`);
            if (!response.ok) throw new Error('Failed to fetch plot');
            const plotData = await response.json();
            plotUrl = plotData.plot_url; // Assuming FastAPI returns a URL to the generated plot
        } catch (error) {
            console.error('Error:', error);
        }
    }

    function initializeMap() {
        if (!mapContainer) return;

        map = new mapboxgl.Map({
            container: mapContainer,
            accessToken: MAPBOX_ACCESS_TOKEN,
            style: 'mapbox://styles/mapbox/dark-v10',
            center: [-117.2361, 32.8753],
            zoom: 9
        });

        map.on('click', (e) => {
            const { lng, lat } = e.lngLat;
            selectedCoordinates = { lat, lon: lng };
            alert(`Selected Coordinates: Latitude ${lat}, Longitude ${lng}`);
        });

        map.scrollZoom.disable();
        map.addControl(new mapboxgl.NavigationControl());

        map.on('load', fetchClimateData); // Fetch data when map is ready
    }

    onMount(() => {
        initializeMap();
    });

    onDestroy(() => {
        if (map) map.remove();
    });
</script>

<!-- HTML for the landing page -->
<div class="landing-page">
    <div class="background-video">
        <video autoplay muted loop class="background-video">
            <source src="/landing background.mp4" type="video/mp4" />
        </video>
    </div>
    <h1>Explore the Impact of Climate Change</h1>
</div>

<!-- Time Index Input Section -->
<div class="time-index-input">
    <label for="time-index">Select Time Index:</label>
    <input type="number" id="time-index" bind:value={timeIndex} min="0" />
</div>

<!-- Crop Selection Dropdown -->
<div class="crop-selection">
    <label for="crop">Select Crop:</label>
    <select id="crop" bind:value={selectedCrop}>
        <option value="" disabled selected>Select a crop</option>
        {#each crops as crop}
            <option value={crop}>{crop}</option>
        {/each}
    </select>
</div>

<!-- Generate Plot Button Below Crop Selection -->
<div class="generate-plot-button">
    <button on:click={generatePlot}>Generate Plot</button>
</div>

<!-- Plot Display Section -->
<div class="plot-display">
    {#if plotUrl}
        <img src={plotUrl} alt="Climate Plot" />
    {:else}
        <p>No plot to display</p>
    {/if}
</div>

<!-- Map and Climate Data Section -->
<div class="page2">
    {#if loading}
        <p>Loading climate data...</p>
    {:else if errorMessage}
        <p class="error">{errorMessage}</p>
    {:else}
        <div class="map-container" bind:this={mapContainer}></div>

        <!-- Display Climate Data -->
        <div class="climate-data">
            <h2>Climate Data</h2>
            <ul>
                {#each climateData as { lat, lon, value }}
                    <li>
                        <strong>Latitude:</strong> {lat}, <strong>Longitude:</strong> {lon}, <strong>Value:</strong> {value}
                    </li>
                {/each}
            </ul>
        </div>
    {/if}
</div>

<!-- CSS styles -->
<style>
    /* Global styles */
    :global(html, body) {
        font-family: Arial, sans-serif;
        scrollbar-width: none;
        background-color: black;
        color: white;
    }

    :global(body::-webkit-scrollbar) {
        display: none;
    }

    .landing-page, h1, h2, p, label, li, .climate-data {
        color: white;
    }

    .landing-page {
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        min-height: 100vh;
    }

    .background-video {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .landing-page h1 {
        font-size: 3rem;
        margin-bottom: 1rem;
        z-index: 1;
    }

    .page2 {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        height: 100vh;
    }

    .map-container {
        padding: 20px;
        text-align: center;
        height: 500px;
        width: 500px;
        position: relative;
        border-radius: 4px;
        border-width: 1px;
        border-color: hsl(240, 4%, 46%);
        margin-bottom: 20px;
    }

    .time-index-input {
        margin-bottom: 20px;
        color: black;
    }

    .time-index-input input {
        padding: 5px;
        margin-right: 10px;
    }

    .crop-selection {
        margin-top: 20px;
        color: black;
    }

    .crop-selection select {
        padding: 5px;
        margin-top: 10px;
    }

    .generate-plot-button {
        margin-top: 20px;
    }

    .generate-plot-button button {
        padding: 5px 10px;
        cursor: pointer;
    }

    .plot-display img {
        width: 100%;
        max-width: 600px;
        margin-top: 20px;
    }

    .climate-data {
        background-color: #f0f0f0;
        padding: 20px;
        border-radius: 8px;
        width: 80%;
        max-width: 600px;
        margin-top: 20px;
    }

    .climate-data h2 {
        text-align: center;
        font-size: 1.5rem;
        margin-bottom: 10px;
    }

    .climate-data ul {
        list-style-type: none;
        padding: 0;
    }

    .climate-data li {
        font-size: 1rem;
        margin: 5px 0;
    }

    .error {
        color: red;
        text-align: center;
        font-size: 1.2rem;
    }
</style>
