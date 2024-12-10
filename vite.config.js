import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import svgr from 'vite-plugin-svgr'
// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svgr(),react()],
  server:{
    proxy:{
      //api ->localhost:5000
      '/api':{
        target:'http://localhost:5000',
        changeOrigin:true,
        secure:false
      },
    },
    build:{
      sourcemap:true,
    }
  },
});
