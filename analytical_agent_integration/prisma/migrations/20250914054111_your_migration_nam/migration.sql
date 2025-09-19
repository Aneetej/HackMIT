/*
  Warnings:

  - You are about to drop the column `teacherId` on the `notes` table. All the data in the column will be lost.

*/
-- DropForeignKey
ALTER TABLE "public"."notes" DROP CONSTRAINT "notes_teacherId_fkey";

-- AlterTable
ALTER TABLE "public"."notes" DROP COLUMN "teacherId";
