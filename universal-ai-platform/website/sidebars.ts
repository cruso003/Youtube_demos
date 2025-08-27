import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'getting-started',
    {
      type: 'category',
      label: 'API Reference',
      items: ['api'],
    },
    {
      type: 'category',
      label: 'Client SDKs',
      items: [
        'sdks/python',
        'sdks/javascript',
      ],
    },
    {
      type: 'category',
      label: 'Guides',
      items: [
        'guides/adapters',
        'guides/deployment',
      ],
    },
    {
      type: 'category',
      label: 'Examples',
      items: [
        'examples/language-learning',
      ],
    },
  ],
};

export default sidebars;
