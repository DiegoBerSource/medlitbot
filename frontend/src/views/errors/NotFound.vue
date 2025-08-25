<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full space-y-8 text-center">
      <div>
        <h1 class="text-9xl font-bold text-gray-300">404</h1>
        <h2 class="mt-2 text-3xl font-bold text-gray-900">Page not found</h2>
        <p class="mt-2 text-gray-600">
          Sorry, we couldn't find the page you're looking for.
        </p>
      </div>
      <div>
        <RouterLink to="/" class="btn-primary">
          Go back home
        </RouterLink>
      </div>
    </div>
  </div>
</template>
