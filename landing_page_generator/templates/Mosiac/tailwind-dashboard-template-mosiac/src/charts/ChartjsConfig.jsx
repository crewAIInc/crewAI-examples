// Import Chart.js
import { Chart, Tooltip } from 'chart.js';
// Import Tailwind config
import { tailwindConfig, hexToRGB } from '../utils/Utils';

Chart.register(Tooltip);

// Define Chart.js default settings
Chart.defaults.font.family = '"Inter", sans-serif';
Chart.defaults.font.weight = 500;
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.displayColors = false;
Chart.defaults.plugins.tooltip.mode = 'nearest';
Chart.defaults.plugins.tooltip.intersect = false;
Chart.defaults.plugins.tooltip.position = 'nearest';
Chart.defaults.plugins.tooltip.caretSize = 0;
Chart.defaults.plugins.tooltip.caretPadding = 20;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.plugins.tooltip.padding = 8;

// Function that generates a gradient for line charts
export const chartAreaGradient = (ctx, chartArea, colorStops) => {
  if (!ctx || !chartArea || !colorStops || colorStops.length === 0) {
    return 'transparent';
  }
  const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
  colorStops.forEach(({ stop, color }) => {
    gradient.addColorStop(stop, color);
  });
  return gradient;
};

export const chartColors = {
  textColor: {
    light: tailwindConfig().theme.colors.gray[400],
    dark: tailwindConfig().theme.colors.gray[500],
  },
  gridColor: {
    light: tailwindConfig().theme.colors.gray[100],
    dark: `rgba(${hexToRGB(tailwindConfig().theme.colors.gray[700])}, 0.6)`,
  },
  backdropColor: {
    light: tailwindConfig().theme.colors.white,
    dark: tailwindConfig().theme.colors.gray[800],
  },
  tooltipTitleColor: {
    light: tailwindConfig().theme.colors.gray[800],
    dark: tailwindConfig().theme.colors.gray[100],
  },
  tooltipBodyColor : {
    light: tailwindConfig().theme.colors.gray[500],
    dark: tailwindConfig().theme.colors.gray[400]
  },
  tooltipBgColor: {
    light: tailwindConfig().theme.colors.white,
    dark: tailwindConfig().theme.colors.gray[700],
  },
  tooltipBorderColor: {
    light: tailwindConfig().theme.colors.gray[200],
    dark: tailwindConfig().theme.colors.gray[600],
  },
};
