<svelte:head>
  <script src="https://accounts.google.com/gsi/client" async defer />
	<script lang="ts">
		const LOGIN_URI = 'https://palm.fly.dev/auth/google/token/signin'

		async function getAuthorization(response: GoogleResponse) {
			const { credential } = response
			const {data, message} = await fetch(LOGIN_URI, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					id_token: credential
				})
			}).then(res => res.json())
			console.log(message)
			if (data.signup_complete) {
				localStorage.setItem('accessToken', data.access_token)
				localStorage.setItem('refresh_token', data.refresh_token)
				window.location.href = '/'
			}
		}
	</script>
</svelte:head>
<main style="width:100vw; height:100vh; display: flex; justify-content:center; align-items:center;">
	<div style="display: flex;">
		<div id="g_id_onload"
				data-client_id="787136138588-q84sqt3gu8ts2td2p6oe6f20d1usabgn.apps.googleusercontent.com"
				data-context="signin"
				data-ux_mode="popup"
				data-callback="getAuthorization"
				data-nonce=""
				data-auto_prompt="false">
		</div>

		<div class="g_id_signin"
				data-type="standard"
				data-shape="rectangular"
				data-theme="outline"
				data-text="signin_with"
				data-size="large"
				data-locale="ko"
				data-logo_alignment="left"
				data-width="400">
		</div>
	</div>
</main>
