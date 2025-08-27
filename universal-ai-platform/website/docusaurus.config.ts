import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Universal AI Agent Platform',
  tagline: 'Integrate multimodal AI agents into any application without building infrastructure',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://cruso003.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/Youtube_demos/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'cruso003', // Usually your GitHub org/user name.
  projectName: 'Youtube_demos', // Usually your repo name.

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
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/cruso003/Youtube_demos/tree/main/universal-ai-platform/website/',
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
      title: 'Universal AI Platform',
      logo: {
        alt: 'Universal AI Platform Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          to: '/docs/api',
          label: 'API Reference',
          position: 'left',
        },
        {
          to: '/docs/examples/language-learning',
          label: 'Examples',
          position: 'left',
        },
        {
          href: 'https://github.com/cruso003/Youtube_demos/tree/main/universal-ai-platform',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
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
          title: 'Examples',
          items: [
            {
              label: 'Language Learning',
              to: '/docs/examples/language-learning',
            },
            {
              label: 'Emergency Services',
              to: '/docs/examples/emergency-services',
            },
            {
              label: 'Custom Adapters',
              to: '/docs/examples/custom-adapters',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/cruso003/Youtube_demos/tree/main/universal-ai-platform',
            },
            {
              label: 'Demo Apps',
              href: 'https://github.com/cruso003/Youtube_demos/tree/main/universal-ai-platform/demos',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Universal AI Platform. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
