import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'NexusAI Documentation',
  tagline: 'The Universal AI Agent Platform for Africa - API Documentation & Developer Guides',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://nexus-docs.bits-innovate.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'cruso003', // Usually your GitHub org/user name.
  projectName: 'nexusai-docs', // Usually your repo name.

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          // Remove edit links for professional deployment
        },
        blog: false, // Disable blog
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    navbar: {
      title: 'NexusAI Docs',
      logo: {
        alt: 'NexusAI Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          href: 'https://nexus.bits-innovate.com',
          label: 'Home',
          position: 'left',
        },
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Documentation',
        },
        {
          to: '/docs/api',
          label: 'API Reference',
          position: 'left',
        },
        {
          to: '/docs/sdks',
          label: 'SDKs',
          position: 'left',
        },
        {
          href: 'https://bits-innovate.com',
          label: 'BITS',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'NexusAI Platform',
          items: [
            {
              label: 'Home',
              href: 'https://nexus.bits-innovate.com',
            },
            {
              label: 'Sign Up',
              href: 'https://nexus.bits-innovate.com/signup',
            },
            {
              label: 'Dashboard',
              href: 'https://nexus.bits-innovate.com/dashboard',
            },
          ],
        },
        {
          title: 'Documentation',
          items: [
            {
              label: 'Getting Started',
              to: '/docs/getting-started',
            },
            {
              label: 'API Reference',
              to: '/docs/api',
            },
            {
              label: 'SDK Documentation',
              to: '/docs/sdks',
            },
          ],
        },
        {
          title: 'SDKs',
          items: [
            {
              label: 'JavaScript SDK',
              href: 'https://www.npmjs.com/package/nexusai-sdk',
            },
            {
              label: 'Python SDK',
              href: 'https://pypi.org/project/nexusai-sdk/',
            },
            {
              label: 'SDK Documentation',
              to: '/docs/sdks',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'BITS',
              href: 'https://bits-innovate.com',
            },
            {
              label: 'Contact Support',
              href: 'mailto:support@nexus.bits-innovate.com',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} NexusAI Platform. Built with ❤️ for Africa by BITS (Building Innovative Technical Solutions).`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
