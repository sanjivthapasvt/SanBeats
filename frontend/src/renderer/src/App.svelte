<script>
  import Router from 'svelte-spa-router'
  import HomePage from './components/pages/HomePage.svelte'
  import SearchBar from './components/navigation/SearchBar.svelte'
  import SearchResults from './components/pages/SearchResults.svelte'
  import Playing from './components/pages/Player.svelte'
  import DownloadPage from './components/pages/DownloadPage.svelte'
  const routes = {
    '/': HomePage,
    '/search': SearchResults,
    '/play': Playing,
    '/download': DownloadPage
  }
</script>

<header>
  <SearchBar />
</header>

<main>
  <Router {routes} />
</main>

<style>
  header {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 1000;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  main {
    padding-top: 50px;
  }
</style>
