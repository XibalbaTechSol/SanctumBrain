const { prisma } = require('./packages/db');

async function test() {
  try {
    console.log('Testing DB update...');
    const res = await prisma.entity.update({
      where: { id: 'admin-9' },
      data: { title: 'Test Update ' + new Date().toISOString() }
    });
    console.log('Update result:', JSON.stringify(res, null, 2));
  } catch (err) {
    console.error('Update failed:', err);
  } finally {
    await prisma.$disconnect();
  }
}

test();
