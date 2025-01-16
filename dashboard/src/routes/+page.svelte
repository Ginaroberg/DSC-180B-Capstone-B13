<script lang="ts">
    import mapboxgl from 'mapbox-gl';
    import 'mapbox-gl/dist/mapbox-gl.css';
    import { onMount, onDestroy } from 'svelte';

    let map: mapboxgl.Map;
    let mapContainer: HTMLElement;
    let selectedCoordinates = { lat: 0, lon: 0 };

    const MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoicTF6b3UiLCJhIjoiY2xzaTQwOXlhMjRyOTJqbW5scHZ0a24ybiJ9.GnA8FZpch2_6h3BBhdCVPg'; // Replace with your Mapbox token



    // Initialize the map
    function initializeMap() {
        map = new mapboxgl.Map({
            container: mapContainer,
            accessToken: MAPBOX_ACCESS_TOKEN,
            style: 'mapbox://styles/mapbox/dark-v10', // Add style
            center: [-117.2361, 32.8753], // Initial center (longitude, latitude)
            zoom: 9
        });

        // Handle click events on the map
        map.on('click', (e) => {
            const { lng, lat } = e.lngLat;
            selectedCoordinates = { lat, lon: lng };
            alert(`Selected Coordinates: Latitude ${lat}, Longitude ${lng}`);
        });

        map.scrollZoom.disable(); // Disable scroll zoom
        map.addControl(new mapboxgl.NavigationControl()); // Add navigation control
    }

    onMount(() => {
        initializeMap(); // Always initialize the map
    });

    onDestroy(() => {
        if (map) {
            map.remove();
        }
    });
</script>









<!--HTML-->


<div class="landing-page">
    <div class="background-video">
        <video autoplay muted loop class="background-video">
            <source src="/landing background.mp4" type="video/mp4" />
        </video>
    </div>
    <h1>Explore the Impact of Climate Change</h1>
</div>

<div class="page2">
    <div class="map-container" bind:this={mapContainer}></div>
</div>















<style>
    :global(html, body) {
        font-family: Arial, sans-serif;
        scrollbar-width: none; /* Hide scrollbar for Firefox */
    }

    :global(body){
        background-color: black;
    }

    :global(body::-webkit-scrollbar) {
        display: none; /* Hide scrollbar for WebKit browsers */
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
        color: white;
        z-index: 1;
    }


    .page2 {
        display: flex;
        justify-content: center;
        align-items: center;
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
    }


</style>
